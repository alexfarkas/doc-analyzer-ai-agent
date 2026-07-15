import logging
import time
from typing import AsyncGenerator

from agent_enums import Assignment, Mode, Role
from db_repository import PromptRepository
from rag_client import ChromaDBClientFactory

from src.doc_analyzer_backend.agent.ai_invocation import ai_invoke_track
from src.doc_analyzer_backend.agent.consumption_counters.token_counter import (
    calculate_tokens_usage,
)
from src.doc_analyzer_backend.agent.context.conversation_storage import (
    ConversationHistory,
)
from src.doc_analyzer_backend.agent.context.prompts_storage import get_prompts
from src.doc_analyzer_backend.agent.context.rag_context import (
    get_prompts_with_rag,
    get_user_prompt_with_rag,
)
from src.doc_analyzer_backend.agent.core.graph_builder import build_graph
from src.doc_analyzer_backend.agent.core.llm_model_manager import LLMModelManager
from src.doc_analyzer_backend.agent.messages_data.agent_data_builder import (
    build_doc_analyse_data,
)
from src.doc_analyzer_backend.agent.messages_data.chat_utils import (
    prepare_chat_messages,
    stream_llm_response,
    finalize_chat_stream,
)
from src.doc_analyzer_backend.agent.messages_data.messages_utils import (
    build_messages,
)
from src.doc_analyzer_backend.agent.models.analysis.agent_analysis_data import (
    AgentAnalysisData,
)
from src.doc_analyzer_backend.config.llm_config import LLMConfig
from src.doc_analyzer_backend.llm.llm_factory import LLMFactory
from src.doc_analyzer_backend.tools.tools import init_tools

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self):
        self.llm = None
        self.tools = None
        self.app = None
        self.llm_config = None

        self._llm_model_manager: LLMModelManager | None = None
        self._history: ConversationHistory = ConversationHistory()

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

        self._history.clear()
        self._history.save(prompts)

        if self._chromadb_client_factory and self._rag_collections_names:
            prompts = await get_prompts_with_rag(
                prompts, self._chromadb_client_factory, self._rag_collections_names
            )
        messages = build_messages(prompts, Mode.ANALYSIS)

        estimated_tokens = calculate_tokens_usage(messages, self.llm_config.model)
        logger.info(f"Estimated input tokens: {estimated_tokens}")

        final_msg, consumption_data = ai_invoke_track(
            agent_id=self.agent_id,
            app=self.app,
            messages=messages,
            provider=self._llm_model_manager.current_provider,
            model=self._llm_model_manager.current_model,
            type_message="doc analysis",
        )

        self._history.save_ai_message(final_msg)

        return build_doc_analyse_data(
            final_msg=final_msg,
            consumption_data=consumption_data,
        )

    async def clarify(
        self,
        ai_answer: str,
        user_message: str,
        model: str | None = None,
    ) -> AgentAnalysisData:
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

        messages = build_messages(prompts, Mode.CLARIFICATION)

        final_msg, consumption_data = ai_invoke_track(
            agent_id=self.agent_id,
            app=self.app,
            messages=messages,
            provider=self._llm_model_manager.current_provider,
            model=self._llm_model_manager.current_model,
            type_message="clarification",
        )

        return build_doc_analyse_data(
            final_msg=final_msg,
            consumption_data=consumption_data,
        )

    async def chat(
        self, user_message: str, model: str | None = None
    ) -> AgentAnalysisData:
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

        messages = build_messages(prompts, Mode.CHAT)

        self._history.trim()

        final_msg, consumption_data = ai_invoke_track(
            agent_id=self.agent_id,
            app=self.app,
            messages=messages,
            provider=self._llm_model_manager.current_provider,
            model=self._llm_model_manager.current_model,
            type_message="chat",
        )

        self._history.save_user_prompt(user_message)
        self._history.save_ai_message(final_msg)

        return build_doc_analyse_data(
            final_msg=final_msg,
            consumption_data=consumption_data,
        )

    async def chat_stream(
        self,
        user_message: str,
        model: str | None = None,
    ) -> AsyncGenerator[str, None]:
        start = time.perf_counter()
        logger.info(f"Agent {self.agent_id}: chat stream is starting...")

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
                    provider=self._llm_model_manager.current_provider,
                    model=self._llm_model_manager.current_model,
                    history=self._history,
                    start_time=start,
                )

    async def get_history(self) -> str:
        return self._history.as_string()

    async def setup_model(self, model: str | None):
        if self._llm_model_manager and self._llm_model_manager.model_is_new(model):
            new_llm = await self._llm_model_manager.setup_model(model)
            self.llm = new_llm
            self.app = build_graph(self.llm, self.tools)
