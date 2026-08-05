from unittest.mock import Mock

import pytest

from src.doc_analyzer_backend.config.app_config import AppConfig
from src.doc_analyzer_backend.config.db_config import DBConfig
from src.doc_analyzer_backend.config.llm_config import LLMConfig
from src.doc_analyzer_backend.config.loader import settings as settings_module
from src.doc_analyzer_backend.config.logger_config import LoggerConfig
from src.doc_analyzer_backend.config.pricing_config import PricingConfig
from src.doc_analyzer_backend.config.provider_config import ProviderConfig
from src.doc_analyzer_backend.config.rag_config import RAGConfig
from src.doc_analyzer_backend.config.service_config import ServiceConfig
from tests.consts.llm import DEFAULT_LLM_PROVIDER, DEFAULT_LLM_MODEL, DEFAULT_LLM_BASE_URL, DEFAULT_LLM_TEMPERATURE, \
    DEFAULT_LLM_MOCK_RESPONSE
from tests.consts.rag import DEFAULT_RAG_PROVIDER, DEFAULT_RAG_MODEL, DEFAULT_RAG_TOP_K, \
    DEFAULT_RAG_SIMILARITY_THRESHOLD, DEFAULT_RAG_PATH, DEFAULT_RAG_USE_VECTOR_DB, DEFAULT_RAG_USE_LOCAL_VECTOR_DB


@pytest.fixture(autouse=True)
def reset_app_settings_cache():
    """
    Сбрасывает кэш синглтона app_settings() перед каждым тестом.
    Гарантирует, что патчи из mock_app_settings применятся корректно.
    """
    settings_module._settings = None
    yield
    settings_module._settings = None


@pytest.fixture
def app_config():
    """App Config mock"""
    config = Mock(AppConfig)
    config.docs_dir = "/app/documents"
    config.max_file_preview_size = 1024 * 1024
    config.allowed_exts = [".txt", ".docx", ".pdf", ".md"]
    return config


@pytest.fixture
def service_config():
    """Service Config mock"""
    config = Mock(ServiceConfig)
    config.host = "127.0.0.1"
    config.port = 8000
    config.timeout_keep_alive = 300
    config.timeout_graceful_shutdown = 300
    config.reload = True
    return config


@pytest.fixture
def llm_config():
    """LLM Config mock"""
    config = Mock(spec=LLMConfig)
    config.provider = DEFAULT_LLM_PROVIDER
    config.model = DEFAULT_LLM_MODEL
    config.base_url = DEFAULT_LLM_BASE_URL
    config.temperature = DEFAULT_LLM_TEMPERATURE
    config.mock_response = DEFAULT_LLM_MOCK_RESPONSE
    return config


@pytest.fixture
def provider_config():
    """Provider Config mock"""
    config = Mock(ProviderConfig)
    config.providers_models = {
        "openai": ["gpt-5-nano", "gpt-4o-mini"],
        "ollama": ["llama3.2"],
    }
    config.get_provider_by_model = Mock(return_value="openai")
    return config


@pytest.fixture
def db_config():
    """DB Config mock"""
    config = Mock(DBConfig)
    config.url = "sqlite:///./data/prompts.db"
    config.use_db_prompts = False
    return config


@pytest.fixture
def rag_config():
    """RAG Config mock"""
    config = Mock(spec=RAGConfig)
    config.embedding_provider = DEFAULT_RAG_PROVIDER
    config.embedding_model = DEFAULT_RAG_MODEL
    config.top_k = DEFAULT_RAG_TOP_K
    config.similarity_threshold = DEFAULT_RAG_SIMILARITY_THRESHOLD
    config.path = DEFAULT_RAG_PATH
    config.use_vector_db = DEFAULT_RAG_USE_VECTOR_DB
    config.use_local_vector_db = DEFAULT_RAG_USE_LOCAL_VECTOR_DB
    return config


@pytest.fixture
def logger_config():
    """Logger Config mock"""
    config = Mock(LoggerConfig)
    config.path = "./logs/backend.log"
    config.level = "INFO"
    config.write_to_file = False
    return config


@pytest.fixture
def pricing_config():
    """Pricing Config mock"""
    config = Mock(PricingConfig)
    config.providers = {
        "openai": {
            "gpt-5-nano": Mock(input=50.0, output=80.0),
            "gpt-4o-mini": Mock(input=100.5, output=120.5),
        },
        "ollama": {"ollama": Mock(input=0.0, output=0.0)},
    }
    return config
