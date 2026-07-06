import json
import logging
import time
from typing import TypedDict, Annotated, Sequence, AsyncGenerator

from agent_enums import Assignment, Mode, Role
from db_repository import PromptRepository
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from rag_client import ChromaDBClientFactory

from agent.conversation_storage import ConversationHistory
from agent.prompts_storage import get_prompts
from agent.rag_context import get_prompts_with_rag, get_user_prompt_with_rag
from api.models.analisys.answer_item import AnswerItem
from api.models.analisys.answer_seq import AnswerSeq
from api.utils.total_token_usage_utils import update_and_get_total_token_usage
from config.llm_config import LLMConfig
from config.provider_config import provider_config
from llm.llm_factory import LLMFactory
from llm.token_counter import (
    calculate_token_usage,
    calculate_cost,
    calculate_tokens_usage,
    calculate_stream_tokens_usage,
)
from llm.token_usage import TokenUsage, create_token_usage
from tools.tools import init_tools

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


class Agent:
    def __init__(self):
        self.llm = None
        self.tools = None
        self.app = None
        self.llm_config = None

        self._provider = None
        self._model = None

        self._history: ConversationHistory = ConversationHistory()
        self._token_usage: TokenUsage = create_token_usage()

        self._prompt_repository: PromptRepository | None = None
        self._chromadb_client_factory: ChromaDBClientFactory | None = None
        self._rag_collections_names: list[str] = []

    @classmethod
    async def create_agent(
        cls,
        llm_config: LLMConfig,
        agent_id: int = 1,
        prompt_repository: PromptRepository | None = None,
        chromadb_client_factory: ChromaDBClientFactory | None = None,
    ) -> Agent:
        instance = cls()
        await instance._initialize(
            llm_config, agent_id, prompt_repository, chromadb_client_factory
        )
        return instance

    async def _initialize(
        self,
        llm_config: LLMConfig,
        agent_id: int = 0,
        prompt_repository: PromptRepository | None = None,
        chromadb_client_factory: ChromaDBClientFactory | None = None,
    ) -> None:
        self.llm_config = llm_config
        self.agent_id = agent_id
        self._prompt_repository = prompt_repository
        self._chromadb_client_factory = chromadb_client_factory

        self.llm = LLMFactory.create_llm(self.llm_config)

        self._provider = llm_config.provider
        self._model = llm_config.model

        self.tools = init_tools()
        self.llm = self.llm.bind_tools(self.tools)
        self.app = self._build_graph()

    def _build_graph(self) -> StateGraph:
        async def agent_node(state: AgentState):
            response = await self.llm.ainvoke(state["messages"])
            return {"messages": [response]}

        workflow = StateGraph(AgentState)
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", ToolNode(self.tools))
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", tools_condition)
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    async def analyze_doc(
        self,
        resources: list[str],
        role: Role,
        assignment: Assignment = Assignment.EXEC,
        model: str | None = None,
        limit: int | None = None,
    ) -> dict:
        start = time.perf_counter()
        logger.info("Doc analysis is starting...")
        if limit:
            logger.info(f"Tokens limit: {limit}")
        else:
            logger.info(f"Tokens limit is not set")

        if model is not None:
            await self.setup_model(model)

        prompts = await get_prompts(
            mode=Mode.ANALYSIS,
            role=role,
            assignment=assignment,
            prompt_repository=self._prompt_repository,
            resources=resources,
        )
        system_prompt, user_prompt = prompts

        logger.debug(f"System prompt: {system_prompt}")
        logger.debug(f"User prompt: {user_prompt}")

        self._token_usage = create_token_usage()

        self._history.clear()
        self._history.save(prompts)

        if self._chromadb_client_factory and self._rag_collections_names:
            prompts = await get_prompts_with_rag(
                prompts, self._chromadb_client_factory, self._rag_collections_names
            )
            system_prompt, user_prompt = prompts

            logger.debug(f"System prompt with RAG:\n{system_prompt}")
            logger.debug(f"User prompt with RAG:\n{user_prompt}")

        text = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

        estimated_tokens = calculate_tokens_usage(text, self.llm_config.model)
        logger.info(f"Estimated input tokens: {estimated_tokens}")

        result = await self.app.ainvoke({"messages": text})
        final_msg = next(
            (m.content for m in reversed(result["messages"]) if m.type == "ai"),
            "No answer from agent",
        )

        logger.debug(f"Answer from model: {final_msg}")

        self._history.save_ai_message(final_msg)

        self._token_usage = calculate_token_usage(result["messages"], self.llm_config)
        cost_rub = calculate_cost(self._token_usage, self.llm_config, "RUB")

        logger.info(f"Doc analysis token usage: {self._token_usage}")
        # logger.info(f"Cost rub: {cost_rub}")

        elapsed = time.perf_counter() - start
        logger.info(f"Doc analysis is completed in {elapsed} seconds")

        return {
            "answer_seq": AnswerSeq(
                answers=[
                    AnswerItem(
                        answer=final_msg,
                        author="exec",
                        status="final",
                        init_status="final",
                    ),
                ],
            ),
            "token_usage": self._token_usage,
            "elapsed": elapsed,
            "cost_rub": cost_rub,
        }

    async def clarify(
        self,
        ai_answer: str,
        user_message: str,
        model: str | None = None,
    ) -> dict:
        start = time.perf_counter()
        logger.info("Clarification is starting...")

        if model is not None:
            await self.setup_model(model)

        logger.debug(f"History system prompt{self._history.system_prompt}")

        init_user_prompt = user_message
        logger.debug(f"User clarification message:\n{init_user_prompt}")

        if self._chromadb_client_factory:
            _, init_user_prompt = await get_prompts_with_rag(
                ("", init_user_prompt),
                self._chromadb_client_factory,
                self._rag_collections_names,
            )
            logger.debug(f"User prompt with RAG in clarification:\n{init_user_prompt}")

        prompts = await get_prompts(
            mode=Mode.CLARIFICATION,
            prompt_repository=self._prompt_repository,
            init_system_prompt=self._history.system_prompt,
            init_user_prompt=init_user_prompt,
            ai_answer=ai_answer,
        )
        system_prompt, user_prompt = prompts

        logger.debug(f"System clarification prompt:\n{system_prompt}")
        logger.debug(f"User clarification prompt:\n{user_prompt}")

        text = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

        result = await self.app.ainvoke({"messages": text})
        final_msg = next(
            (m.content for m in reversed(result["messages"]) if m.type == "ai"),
            "No answer from agent",
        )

        logger.debug(f"Answer from model:\n{final_msg}")

        clarification_token_usage = calculate_token_usage(
            result["messages"], self.llm_config
        )
        self._token_usage.add_usage(clarification_token_usage)
        logger.info(f"Clarification token usage: {clarification_token_usage}")
        logger.info(f"Overall token usage: {self._token_usage}")

        elapsed = time.perf_counter() - start
        logger.info(f"Clarification is completed in {elapsed} seconds")

        return {
            "answer_seq": {
                "answers": [
                    {
                        "answer": final_msg,
                        "author": "exec",
                        "status": "final",
                        "init_status": "final",
                    },
                ]
            },
            "token_usage": self._token_usage,
            "elapsed": elapsed,
            "cost_rub": 0,
        }

    async def chat(self, user_message: str, model: str | None = None) -> dict:
        start = time.perf_counter()
        logger.info("Chat is starting...")

        if model is not None:
            await self.setup_model(model)

        logger.debug(f"History system prompt{self._history.system_prompt}")

        init_user_prompt = user_message
        logger.debug(f"User prompt in chat:\n{init_user_prompt}")

        if self._chromadb_client_factory:
            init_user_prompt = await get_user_prompt_with_rag(
                init_user_prompt,
                self._history,
                self._chromadb_client_factory,
                self._rag_collections_names,
            )
            logger.debug(f"User prompt with RAG in chat:\n{init_user_prompt}")

        prompts = await get_prompts(
            mode=Mode.CHAT,
            prompt_repository=self._prompt_repository,
            init_system_prompt=self._history.system_prompt,
            init_user_prompt=init_user_prompt,
            history=self._history.as_string(),
        )
        system_prompt, user_prompt = prompts

        text = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

        logger.debug(f"System chat prompt:\n{system_prompt}")
        logger.debug(f"User chat prompt with history:\n{user_prompt}")

        self._history.trim()

        result = await self.app.ainvoke({"messages": text})
        final_msg = next(
            (m.content for m in reversed(result["messages"]) if m.type == "ai"),
            "No answer from agent",
        )

        logger.debug(f"Answer from model:\n{final_msg}")

        self._history.save_user_prompt(user_message)
        self._history.save_ai_message(final_msg)

        chat_token_usage = calculate_token_usage(result["messages"], self.llm_config)
        self._token_usage.add_usage(chat_token_usage)
        logger.info(f"Chat token usage: {self._token_usage}")
        logger.info(f"Overall token usage: {self._token_usage}")

        elapsed = time.perf_counter() - start
        logger.info(f"Chat is completed in {elapsed} seconds")

        return {
            "answer_seq": {
                "answers": [
                    {
                        "answer": final_msg,
                        "author": "exec",
                        "status": "final",
                        "init_status": "final",
                    },
                ]
            },
            "token_usage": self._token_usage,
            "elapsed": elapsed,
            "cost_rub": 0,
        }

    async def chat_stream(
        self, user_message: str,
        model: str | None = None,
    ) -> AsyncGenerator[str, None]:
        start = time.perf_counter()
        logger.info("Chat stream is starting...")

        if model is not None:
            await self.setup_model(model)

        logger.debug(f"History system prompt{self._history.system_prompt}")

        init_user_prompt = user_message
        logger.debug(f"User prompt in chat:\n{init_user_prompt}")

        if self._chromadb_client_factory:
            init_user_prompt = await get_user_prompt_with_rag(
                init_user_prompt,
                self._history,
                self._chromadb_client_factory,
                self._rag_collections_names,
            )
            logger.debug(f"User prompt with RAG in chat:\n{init_user_prompt}")

        prompts = await get_prompts(
            mode=Mode.CHAT,
            prompt_repository=self._prompt_repository,
            init_system_prompt=self._history.system_prompt,
            init_user_prompt=init_user_prompt,
            history=self._history.as_string(),
        )
        system_prompt, user_prompt = prompts

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        logger.debug(f"System chat prompt: {system_prompt}")
        logger.debug(f"User chat prompt with history: {user_prompt}")

        self._history.trim()

        accumulated_content = []

        try:
            async for chunk in self.llm.astream(messages):
                content = None

                if hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                elif isinstance(chunk, dict) and "content" in chunk:
                    content = chunk["content"]
                elif hasattr(chunk, "delta") and hasattr(chunk.delta, "content"):
                    content = chunk.delta.content

                if content:
                    accumulated_content.append(content)
                    yield content

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"\n\n[Ошибка генерации ответа: {str(e)}]"
            return
        finally:
            full_answer = "".join(accumulated_content)
            if full_answer:
                self._history.save_user_prompt(user_message)
                self._history.save_ai_message(full_answer)

                input_tokens = await calculate_stream_tokens_usage(
                    f"{system_prompt}\n{user_prompt}", self._model
                )
                output_tokens = await calculate_stream_tokens_usage(
                    full_answer, self._model
                )

                chat_stream_token_usage = create_token_usage(
                    input_tokens=input_tokens, output_tokens=output_tokens
                )
                self._token_usage.add_usage(chat_stream_token_usage)
                logger.info(f"Chat stream token usage: {chat_stream_token_usage}")
                logger.info(f"Overall token usage: {self._token_usage}")

                elapsed = time.perf_counter() - start
                logger.info(f"Chat stream is completed in {elapsed} seconds")

                total_token_usage = await update_and_get_total_token_usage(self._token_usage)

                result = json.dumps(
                    {
                        "token_usage": self._token_usage.model_dump(),
                        "total_token_usage": total_token_usage.model_dump(),
                        "elapsed": elapsed,
                        "cost_rub": 0,
                    }
                )
                yield f"\n__METADATA__:{result}"

    async def get_history(self) -> str:
        return self._history.as_string()

    async def setup_model(self, new_model: str):
        new_provider = provider_config.get_provider_by_model(new_model)

        if self._provider == new_provider and self._model == new_model:
            return

        try:
            logger.info(
                f"Changing LLM model from {self._provider}/{self._model} to {new_provider}/{new_model}..."
            )

            new_llm = LLMFactory.create_llm(self.llm_config, new_provider, new_model)
            new_llm = new_llm.bind_tools(self.tools)

            self.llm = new_llm
            self.app = self._build_graph()

            logger.info(f"LLM model changed to {new_provider}/{new_model}")
        except Exception as e:
            logger.error(f"Error while changing LLM model: {e}")
