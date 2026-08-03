from contextlib import contextmanager
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from src.doc_analyzer_backend.api.api import app
from src.doc_analyzer_backend.api.dependencies.dependencies import get_user_session
from src.doc_analyzer_backend.api.models.config.config_response import ConfigResponse
from src.doc_analyzer_backend.session.data.user_session import UserSession


@pytest.fixture
def backend_config():
    """Backend configuration mock for GET /config endpoint"""
    config = Mock(spec=ConfigResponse)
    config.roles = []
    return config


@pytest.fixture
def test_api_client(mock_agent, mock_council):
    """API TestClient with agent and council mocks"""
    with create_test_client(mock_agent=mock_agent, mock_council=mock_council) as client:
        yield client


@pytest.fixture
def test_api_client_no_agent(mock_agent, mock_council):
    """API TestClient with council mock but without agent mock"""
    with create_test_client(mock_agent=None, mock_council=mock_council) as client:
        yield client


@contextmanager
def create_test_client(mock_agent, mock_council):
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
def test_api_client_real_session(mock_agent, mock_council, mocker):
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
    mock_agent, mock_council, mock_llm_config, mock_rag_config, mocker
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
    mocker.patch(
        "src.doc_analyzer_backend.api.routers.system_router.llm_config", mock_llm_config
    )
    mocker.patch(
        "src.doc_analyzer_backend.api.routers.system_router.rag_config", mock_rag_config
    )

    return {
        "session": mock_session,
        "agent": mock_agent,
        "council": mock_council,
        "llm_config": mock_llm_config,
        "rag_config": mock_rag_config,
    }
