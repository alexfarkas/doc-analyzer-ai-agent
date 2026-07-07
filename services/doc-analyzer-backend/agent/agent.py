import logging
import time
from typing import AsyncGenerator

from agent_enums import Assignment, Mode, Role
from db_repository import PromptRepository
from rag_client import ChromaDBClientFactory

from agent.core.llm_model_manager import LLMModelManager
from agent.messages_data.chat_utils import (
    prepare_chat_messages,
    stream_llm_response,
    finalize_chat_stream,
)
from agent.messages_data.messages_utils import build_messages, extract_final_answer
from agent.messages_data.agent_data_builder import build_doc_analyse_data
from agent.context.conversation_storage import ConversationHistory
from agent.context.prompts_storage import get_prompts
from agent.context.rag_context import get_prompts_with_rag, get_user_prompt_with_rag
from agent.core.graph_builder import build_graph
from agent.models.agent_analysis_data import AgentAnalysisData
from config.llm_config import LLMConfig
from llm.llm_factory import LLMFactory
from llm.tokens.token_counter import (
    calculate_token_usage,
    calculate_cost,
    calculate_tokens_usage,
)
from llm.tokens.token_usage import TokenUsage, create_token_usage
from tools.tools import init_tools

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self):
        self.llm = None
        self.tools = None
        self.app = None
        self.llm_config = None

        self._llm_model_manager: LLMModelManager | None = None
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

        self.tools = init_tools()
        self.llm = self.llm.bind_tools(self.tools)
        self.app = build_graph(self.llm, self.tools)

        self._llm_model_manager = LLMModelManager(
            llm_config=llm_config,
            tools=self.tools,
        )

    async def analyze_doc(
        self,
        resources: list[str],
        role: Role,
        assignment: Assignment = Assignment.EXEC,
        model: str | None = None,
        limit: int | None = None,
    ) -> AgentAnalysisData:
        start = time.perf_counter()
        logger.info("Doc analysis is starting...")
        if limit:
            logger.info(f"Tokens limit: {limit}")
        else:
            logger.info("Tokens limit is not set")

        await self.setup_model(model)

        prompts = await get_prompts(
            mode=Mode.ANALYSIS,
            role=role,
            assignment=assignment,
            prompt_repository=self._prompt_repository,
            resources=resources,
        )

        self._token_usage = create_token_usage()

        self._history.clear()
        self._history.save(prompts)

        if self._chromadb_client_factory and self._rag_collections_names:
            prompts = await get_prompts_with_rag(
                prompts, self._chromadb_client_factory, self._rag_collections_names
            )
        text = build_messages(prompts, Mode.ANALYSIS)

        estimated_tokens = calculate_tokens_usage(text, self.llm_config.model)
        logger.info(f"Estimated input tokens: {estimated_tokens}")

        result = await self.app.ainvoke({"messages": text})
        final_msg = await extract_final_answer(result["messages"])

        self._history.save_ai_message(final_msg)

        self._token_usage = calculate_token_usage(result["messages"], self.llm_config)
        cost_rub = calculate_cost(self._token_usage, self.llm_config, "RUB")

        logger.info(f"Doc analysis token usage: {self._token_usage}")
        # logger.info(f"Cost rub: {cost_rub}")

        elapsed = time.perf_counter() - start
        logger.info(f"Doc analysis is completed in {elapsed} seconds")

        return build_doc_analyse_data(
            final_msg=final_msg,
            token_usage=self._token_usage,
            elapsed=elapsed,
            cost_rub=0,
        )

    async def clarify(
        self,
        ai_answer: str,
        user_message: str,
        model: str | None = None,
    ) -> AgentAnalysisData:
        start = time.perf_counter()
        logger.info("Clarification is starting...")

        await self.setup_model(model)

        logger.debug(f"History system prompt{self._history.system_prompt}")

        init_user_prompt = user_message
        logger.debug(f"User clarification message:\n{init_user_prompt}")

        if self._chromadb_client_factory and self._rag_collections_names:
            _, init_user_prompt = await get_prompts_with_rag(
                ("", init_user_prompt),
                self._chromadb_client_factory,
                self._rag_collections_names,
            )

        prompts = await get_prompts(
            mode=Mode.CLARIFICATION,
            prompt_repository=self._prompt_repository,
            init_system_prompt=self._history.system_prompt,
            init_user_prompt=init_user_prompt,
            ai_answer=ai_answer,
        )

        text = build_messages(prompts, Mode.CLARIFICATION)

        result = await self.app.ainvoke({"messages": text})
        final_msg = await extract_final_answer(result["messages"])

        logger.debug(f"Answer from model:\n{final_msg}")

        clarification_token_usage = calculate_token_usage(
            result["messages"], self.llm_config
        )
        self._token_usage.add_usage(clarification_token_usage)
        logger.info(f"Clarification token usage: {clarification_token_usage}")
        logger.info(f"Overall token usage: {self._token_usage}")

        elapsed = time.perf_counter() - start
        logger.info(f"Clarification is completed in {elapsed} seconds")

        return build_doc_analyse_data(
            final_msg=final_msg,
            token_usage=self._token_usage,
            elapsed=elapsed,
            cost_rub=0,
        )

    async def chat(
        self, user_message: str, model: str | None = None
    ) -> AgentAnalysisData:
        start = time.perf_counter()
        logger.info("Chat is starting...")

        await self.setup_model(model)

        logger.debug(f"History system prompt{self._history.system_prompt}")

        init_user_prompt = user_message
        logger.debug(f"User prompt in chat:\n{init_user_prompt}")

        if self._chromadb_client_factory and self._rag_collections_names:
            init_user_prompt = await get_user_prompt_with_rag(
                init_user_prompt,
                self._history,
                self._chromadb_client_factory,
                self._rag_collections_names,
            )

        prompts = await get_prompts(
            mode=Mode.CHAT,
            prompt_repository=self._prompt_repository,
            init_system_prompt=self._history.system_prompt,
            init_user_prompt=init_user_prompt,
            history=self._history.as_string(),
        )

        text = build_messages(prompts, Mode.CHAT)

        self._history.trim()

        result = await self.app.ainvoke({"messages": text})
        final_msg = await extract_final_answer(result["messages"])

        logger.debug(f"Answer from model:\n{final_msg}")

        self._history.save_user_prompt(user_message)
        self._history.save_ai_message(final_msg)

        chat_token_usage = calculate_token_usage(result["messages"], self.llm_config)
        self._token_usage.add_usage(chat_token_usage)

        logger.info(f"Chat token usage: {self._token_usage}")
        logger.info(f"Overall token usage: {self._token_usage}")

        elapsed = time.perf_counter() - start
        logger.info(f"Chat is completed in {elapsed} seconds")

        return build_doc_analyse_data(
            final_msg=final_msg,
            token_usage=self._token_usage,
            elapsed=elapsed,
            cost_rub=0,
        )

    async def chat_stream(
        self,
        user_message: str,
        model: str | None = None,
    ) -> AsyncGenerator[str, None]:
        start = time.perf_counter()
        logger.info("Chat stream is starting...")

        await self.setup_model(model)

        logger.debug(f"History system prompt{self._history.system_prompt}")

        messages = await prepare_chat_messages(
            user_message=user_message,
            history=self._history,
            prompt_repository=self._prompt_repository,
            chromadb_client_factory=self._chromadb_client_factory,
            rag_collections_names=self._rag_collections_names,
        )

        self._history.trim()

        accumulated_content = []
        try:
            async for chunk in stream_llm_response(
                llm=self.llm,
                messages=messages,
                accumulated_content=accumulated_content,
            ):
                yield chunk
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"\n\n[Ошибка генерации ответа: {str(e)}]"
            return
        finally:
            full_answer = "".join(accumulated_content)
            if full_answer:
                finalize_chat_stream(
                    user_message=user_message,
                    full_answer=full_answer,
                    messages=messages,
                    model=self._llm_model_manager.current_model,
                    history=self._history,
                    token_usage=self._token_usage,
                    start_time=start,
                )

    async def get_history(self) -> str:
        return self._history.as_string()

    async def setup_model(self, model: str | None):
        if self._llm_model_manager and self._llm_model_manager.model_is_new(model):
            new_llm = await self._llm_model_manager.setup_model(model)
            self.llm = new_llm
            self.app = build_graph(self.llm, self.tools)
