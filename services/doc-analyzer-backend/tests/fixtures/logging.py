from unittest.mock import patch

import pytest

from src.doc_analyzer_backend.api.config import logger_setup


@pytest.fixture(autouse=True)
def mock_logger_setup():
    """Turn off logger in tests to avoid conflicts"""
    with patch.object(logger_setup, "setup_logging"):
        yield
