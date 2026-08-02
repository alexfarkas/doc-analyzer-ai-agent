import logging
import uuid
from datetime import datetime, timezone

from db_repository import PromptRepository
from rag_client import ChromaDBClientFactory

from src.doc_analyzer_backend.agent.agent import Agent
from src.doc_analyzer_backend.agent.council.council import Council
from src.doc_analyzer_backend.config.db_config import db_config
from src.doc_analyzer_backend.config.llm_config import llm_config
from src.doc_analyzer_backend.config.rag_config import rag_config
from src.doc_analyzer_backend.session.data.user_session import UserSession

logger = logging.getLogger(__name__)


class UserManager:
    def __init__(self):
        self._user_sessions: dict[str, UserSession] = {}

    async def create_session(self) -> UserSession:
        session_id = str(uuid.uuid4())

        prompt_repository = _create_prompt_repository()
        chromadb_client_factory = _create_chromadb_client_factory()

        logger.info("Agent initialization")
        agent = await Agent.create_agent(
            llm_config=llm_config,
            prompt_repository=prompt_repository,
            chromadb_client_factory=chromadb_client_factory,
        )
        logger.info("Agent initialized")

        logger.info("Council initialization")
        council = await Council.init_council(
            prompt_repository=prompt_repository,
            chromadb_client_factory=chromadb_client_factory,
        )
        logger.info("Council initialized")

        session = UserSession(
            session_id=session_id,
            agent=agent,
            council=council,
        )
        self._user_sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> UserSession | None:
        return self._user_sessions.get(session_id)

    def get_or_create_session(self, session_id: str) -> UserSession:
        session = self._user_sessions.get(session_id)
        if session:
            return session
        return self._create_session_with_id(session_id)

    def delete_session(self, session_id: str) -> bool:
        if session_id in self._user_sessions:
            del self._user_sessions[session_id]
            return True
        return False

    def cleanup_inactive(self, max_age_seconds: int = 3600) -> int:
        now = datetime.now(timezone.utc)
        to_delete = []
        for session_id, session in self._user_sessions.items():
            age = (now - session.last_active_at).total_seconds()
            if age > max_age_seconds:
                to_delete.append(session_id)
        for session_id in to_delete:
            del self._user_sessions[session_id]
        return len(to_delete)

    def _create_session_with_id(self, session_id: str) -> UserSession:
        session = UserSession(session_id=session_id)
        self._user_sessions[session_id] = session
        return session


def _create_prompt_repository() -> PromptRepository | None:
    prompt_repository = None
    if db_config.use_db_prompts:
        logger.info("Initializing DB prompts repository...")
        prompt_repository = PromptRepository(db_config.url)
        logger.info("DB prompts repository initialized")
    else:
        logger.info("Using local prompts")
    return prompt_repository


def _create_chromadb_client_factory() -> ChromaDBClientFactory | None:
    chromadb_client_factory = None
    if rag_config.use_vector_db:
        logger.info("Initializing ChromaDB client factory for RAG...")
        chromadb_client_factory = ChromaDBClientFactory(rag_config)
        logger.info("ChromaDB client factory for RAG initialized")
    else:
        logger.info("No RAG is used")
    return chromadb_client_factory


user_manager = UserManager()
