import logging
from typing import AsyncGenerator

from agent_enums import Assignment, Role
from db_repository import PromptRepository
from rag_client import ChromaDBClientFactory

from src.doc_analyzer_backend.agent.agent_ai_invocation.chatter import agent_chat
from src.doc_analyzer_backend.agent.agent_ai_invocation.clarificator import agent_clarify
from src.doc_analyzer_backend.agent.agent_ai_invocation.doc_analyzer import agent_analyze_doc
from src.doc_analyzer_backend.agent.agent_ai_invocation.stream_chatter import agent_chat_stream
from src.doc_analyzer_backend.agent.context.conversation_storage import (
    ConversationHistory,
)
from src.doc_analyzer_backend.agent.core.graph_builder import build_graph
from src.doc_analyzer_backend.agent.core.llm_model_manager import LLMModelManager
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
        await self.setup_model(model)

        return await agent_analyze_doc(
            agent_id=self.agent_id,
            app=self.app,
            resources=resources,
            role=role,
            assignment=assignment,
            provider=self._llm_model_manager.current_provider,
            model=self._llm_model_manager.current_model,
            limit=limit,
            history=self._history,
            prompt_repository=self._prompt_repository,
            chromadb_client_factory=self._chromadb_client_factory,
            rag_collections_names=self._rag_collections_names,
        )

    async def clarify(
        self,
        ai_answer: str,
        user_message: str,
        answer_index: int,
        model: str | None = None,
    ) -> AgentAnalysisData:
        await self.setup_model(model)

        return await agent_clarify(
            agent_id=self.agent_id,
            app=self.app,
            ai_answer=ai_answer,
            user_message=user_message,
            answer_index=answer_index,
            provider=self._llm_model_manager.current_provider,
            model=self._llm_model_manager.current_model,
            history=self._history,
            prompt_repository=self._prompt_repository,
            chromadb_client_factory=self._chromadb_client_factory,
            rag_collections_names=self._rag_collections_names,
        )

    async def chat(
        self, user_message: str, model: str | None = None
    ) -> AgentAnalysisData:
        await self.setup_model(model)

        return await agent_chat(
            agent_id=self.agent_id,
            app=self.app,
            user_message=user_message,
            provider=self._llm_model_manager.current_provider,
            model=self._llm_model_manager.current_model,
            history=self._history,
            prompt_repository=self._prompt_repository,
            chromadb_client_factory=self._chromadb_client_factory,
            rag_collections_names=self._rag_collections_names,
        )

    async def chat_stream(
        self,
        user_message: str,
        model: str | None = None,
    ) -> AsyncGenerator[str, None]:
        await self.setup_model(model)

        return agent_chat_stream(
            agent_id=self.agent_id,
            user_message=user_message,
            llm=self.llm,
            provider=self._llm_model_manager.current_provider,
            model=self._llm_model_manager.current_model,
            history=self._history,
            prompt_repository=self._prompt_repository,
            chromadb_client_factory=self._chromadb_client_factory,
            rag_collections_names=self._rag_collections_names,
        )

    async def get_history(self) -> str:
        return self._history.as_string()

    async def setup_model(self, model: str | None):
        if self._llm_model_manager and self._llm_model_manager.model_is_new(model):
            new_llm = await self._llm_model_manager.setup_model(model)
            self.llm = new_llm
            self.app = build_graph(self.llm, self.tools)
