from unittest.mock import Mock

import pytest

from src.doc_analyzer_backend.api.exceptions.exceptions import (
    AgentFileTooLargeForPreviewError,
)
from tests.consts.preview import (
    DEFAULT_PREVIEW_FILE_PATH,
    MAX_PREVIEW_FILE_SIZE,
    DEFAULT_PREVIEW_FILENAME_WITH_EXT,
)


@pytest.fixture
def mock_file_preview(mocker):
    """
    Function 'file_preview' mock

    Returns:
        Function that setup mock with required result
    """

    def _mock_preview(payload: dict) -> Mock:
        return mocker.patch(
            "src.doc_analyzer_backend.api.routers.data_sources_router.file_preview",
            return_value=payload,
        )

    return _mock_preview


@pytest.fixture
def mock_preview_with_error(mocker):
    """
    Function 'file_preview' mock with error

    Returns:
        Function that setup mock with required error
    """

    def _mock_preview_error(
        error_class: type,
        file_path: str = f"{DEFAULT_PREVIEW_FILE_PATH}/{DEFAULT_PREVIEW_FILENAME_WITH_EXT}",
    ) -> Mock:
        return mocker.patch(
            "src.doc_analyzer_backend.api.routers.data_sources_router.file_preview",
            side_effect=error_class(file_path=file_path),
        )

    return _mock_preview_error


@pytest.fixture
def mock_preview_with_file_too_large_error(mocker):
    """
    Function 'file_preview' mock with too large file error

    Returns:
        Function that setup mock with too large file error
    """

    def _mock_preview_error(
        file_path: str = f"{DEFAULT_PREVIEW_FILE_PATH}/{DEFAULT_PREVIEW_FILENAME_WITH_EXT}",
    ) -> Mock:
        return mocker.patch(
            "src.doc_analyzer_backend.api.routers.data_sources_router.file_preview",
            side_effect=AgentFileTooLargeForPreviewError(
                file_path=file_path, file_size=MAX_PREVIEW_FILE_SIZE * 2
            ),
        )

    return _mock_preview_error
