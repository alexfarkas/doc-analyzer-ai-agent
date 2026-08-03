from unittest.mock import mock_open

import pytest


@pytest.fixture
def mock_file_system(mocker):
    """
    File system mock

    Returns:
        Patched builtins.open for tests not to create real files
    """
    return mocker.patch("builtins.open", mock_open())
