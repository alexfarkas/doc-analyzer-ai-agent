from unittest.mock import Mock

import pytest

from src.doc_analyzer_backend.api.exceptions.exceptions import (
    AgentFileInsteadOfDirectoryError,
)
from tests.consts.filelist import DEFAULT_FILELIST_PATH


@pytest.fixture
def mock_filelist(mocker):
    """
    Function 'list_files' mock

    Returns:
        Function that setup mock with required result
    """

    def _mock_list_files(filelist: dict) -> Mock:
        return mocker.patch(
            "src.doc_analyzer_backend.api.routers.data_sources_router.list_files",
            return_value=filelist,
        )

    return _mock_list_files


@pytest.fixture
def mock_filelist_with_file_instead_of_dir_error(mocker):
    """
    Function 'list_files' mock with file instead of directory error

    Returns:
        Function that setup mock with file instead of directory error
    """

    def _mock_list_files_error(dir_path: str = f"{DEFAULT_FILELIST_PATH}") -> Mock:
        return mocker.patch(
            "src.doc_analyzer_backend.api.routers.data_sources_router.list_files",
            side_effect=AgentFileInsteadOfDirectoryError(dir_path=dir_path),
        )

    return _mock_list_files_error


@pytest.fixture
def mock_filelist_with_exception(mocker):
    """
    Function 'list_files' mock with exception

    Returns:
        Function that setup mock with exception
    """

    def _mock_list_files_exception(error_message: str = "Unhandled exception") -> Mock:
        return mocker.patch(
            "src.doc_analyzer_backend.api.routers.data_sources_router.list_files",
            side_effect=Exception(error_message),
        )

    return _mock_list_files_exception
