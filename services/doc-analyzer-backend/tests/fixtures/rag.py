from unittest.mock import Mock

import pytest

from src.doc_analyzer_backend.config.rag_config import RAGConfig
from tests.consts.rag import (
    DEFAULT_RAG_PROVIDER,
    DEFAULT_RAG_MODEL,
    DEFAULT_RAG_TOP_K,
    DEFAULT_RAG_SIMILARITY_THRESHOLD,
    DEFAULT_RAG_PATH,
    DEFAULT_RAG_USE_LOCAL_VECTOR_DB,
    DEFAULT_RAG_USE_VECTOR_DB,
)


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
def mock_rag_config(rag_config, mocker):
    mocker.patch(
        "src.doc_analyzer_backend.api.routers.system_router.rag_config", rag_config
    )
    return rag_config
