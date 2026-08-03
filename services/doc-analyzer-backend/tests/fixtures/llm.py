from unittest.mock import Mock

import pytest

from src.doc_analyzer_backend.config.llm_config import LLMConfig
from tests.consts.llm import (
    DEFAULT_LLM_PROVIDER,
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_BASE_URL,
    DEFAULT_LLM_TEMPERATURE,
    DEFAULT_LLM_MOCK_RESPONSE,
)


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
def mock_llm_config(llm_config, mocker):
    mocker.patch(
        "src.doc_analyzer_backend.api.routers.system_router.llm_config", llm_config
    )
    return llm_config
