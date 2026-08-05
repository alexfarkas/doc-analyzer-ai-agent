from contextlib import contextmanager
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from src.doc_analyzer_backend.api.api import app
from src.doc_analyzer_backend.api.dependencies.dependencies import get_user_session
from src.doc_analyzer_backend.api.models.config.config_response import ConfigResponse
from src.doc_analyzer_backend.config.loader.settings import AppSettings
from src.doc_analyzer_backend.session.data.user_session import UserSession

_APP_SETTINGS_IMPORT_LOCATIONS = [
    "src.doc_analyzer_backend.api.exceptions.exceptions",
    "src.doc_analyzer_backend.api.routers.system_router",
    "src.doc_analyzer_backend.api.routers.doc_analysis_router",
    "src.doc_analyzer_backend.api.routers.data_sources_router",
    "src.doc_analyzer_backend.api.routers.tokens_router",
    "src.doc_analyzer_backend.api.routers.user_session_router",
    "src.doc_analyzer_backend.agent.consumption_counters.cost_counter",
    "src.doc_analyzer_backend.agent.core.llm_model_manager",
    "src.doc_analyzer_backend.agent.council.council",
    "src.doc_analyzer_backend.components.file_manager.file_manager",
    "src.doc_analyzer_backend.components.preview_reader.preview_reader",
    "src.doc_analyzer_backend.components.uploader.file_uploader",
    "src.doc_analyzer_backend.main",
    "src.doc_analyzer_backend.session.user_manager",
    "src.doc_analyzer_backend.tools.tools",
]


@pytest.fixture
def backend_config():
    """Backend configuration mock for GET /config endpoint"""
    config = Mock(spec=ConfigResponse)
    config.roles = []
    return config


@pytest.fixture
def mock_app_settings(
    app_config,
    service_config,
    llm_config,
    provider_config,
    db_config,
    rag_config,
    logger_config,
    pricing_config,
    mocker,
):
    """
    Мок AppSettings — единая точка управления конфигурацией в тестах.

    Создает мок AppSettings с подмененными полями llm и rag,
    и патчит функцию app_settings() во всех модулях, где она импортирована.
    """
    settings = Mock(spec=AppSettings)

    settings.app = app_config
    settings.service = service_config
    settings.llm = llm_config
    settings.provider = provider_config
    settings.db = db_config
    settings.rag = rag_config
    settings.logger = logger_config
    settings.pricing = pricing_config

    mocker.patch(
        "src.doc_analyzer_backend.config.loader.settings.app_settings",
        return_value=settings,
    )

    for module_path in _APP_SETTINGS_IMPORT_LOCATIONS:
        try:
            mocker.patch(f"{module_path}.app_settings", return_value=settings)
        except (AttributeError, Exception):
            pass

    return settings


@pytest.fixture
def test_api_client(mock_app_settings, mock_agent, mock_council):
    """API TestClient with agent and council mocks"""
    with create_test_client(
        mock_app_settings=mock_app_settings,
        mock_agent=mock_agent,
        mock_council=mock_council,
    ) as client:
        yield client


@pytest.fixture
def test_api_client_no_agent(mock_app_settings, mock_agent, mock_council):
    """API TestClient with council mock but without agent mock"""
    with create_test_client(
        mock_app_settings=mock_app_settings,
        mock_agent=None,
        mock_council=mock_council,
    ) as client:
        yield client


@contextmanager
def create_test_client(mock_app_settings, mock_agent, mock_council):
    """API TestClient with required mocks"""
    mock_session = UserSession(
        session_id="mock-test-session",
        agent=mock_agent,
        council=mock_council,
    )

    def override_get_user_session():
        return mock_session

    app.dependency_overrides[get_user_session] = override_get_user_session

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def test_api_client_real_session(mock_app_settings, mock_agent, mock_council, mocker):
    mock_session = UserSession(
        session_id="real-test-session",
        agent=mock_agent,
        council=mock_council,
    )
    mock_user_manager = mocker.patch("src.doc_analyzer_backend.session.user_manager.user_manager")
    mock_user_manager.create_session = mocker.AsyncMock(return_value=mock_session)
    mock_user_manager.get_session = mocker.Mock(return_value=None)

    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture
def mock_dependencies(
    mock_app_settings, mock_agent, mock_council, mock_llm_config, mock_rag_config, mocker
):
    """Mock all dependencies"""
    mock_session = UserSession(
        session_id="mock-test-session",
        agent=mock_agent,
        council=mock_council,
    )

    mocker.patch(
        "src.doc_analyzer_backend.api.dependencies.dependencies.get_user_session",
        return_value=mock_session,
    )

    return {
        "session": mock_session,
        "agent": mock_agent,
        "council": mock_council,
        "app_settings": mock_app_settings,
        "llm_config": mock_app_settings.llm,
        "rag_config": mock_app_settings.rag,
    }
