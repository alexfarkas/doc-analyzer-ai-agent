from unittest.mock import Mock

import httpx2
import pytest

from tests.consts.files import DEFAULT_FILENAME_WITH_EXT, DEFAULT_FILE_PATH
from tests.consts.urls import DEFAULT_URL
from tests.factories.mocks import make_upload_result_mock


@pytest.fixture
def mock_upload_file(mocker):
    """
    Function 'upload_file' mock

    Returns:
        Function that setup mock with required result
    """

    def _mock_upload(
        path: str | None = None,
        filename: str = DEFAULT_FILENAME_WITH_EXT,
    ) -> Mock:
        file_path = f"{DEFAULT_FILE_PATH}/{filename}" if path is None else path
        return mocker.patch(
            "src.doc_analyzer_backend.api.routers.data_sources_router.upload_file",
            return_value=make_upload_result_mock(
                file_path=file_path, filename=filename
            ),
        )

    return _mock_upload


@pytest.fixture
def mock_upload_from_url(mocker):
    """
    Function 'upload_content_from_url' mock

    Returns:
        Function that setup mock with required result
    """

    def _mock_upload(html: str) -> Mock:
        return mocker.patch(
            "src.doc_analyzer_backend.api.routers.data_sources_router.upload_content_from_url",
            return_value=html,
        )

    return _mock_upload


@pytest.fixture
def mock_upload_from_url_with_http_error(mocker):
    """
    Function 'upload_content_from_url' mock with HTTP error

    Returns:
        Function that setup mock with required HTTP error
    """

    def _mock_upload_error(status_code: int, error_message: str) -> Mock:
        mock_response = httpx2.Response(
            status_code=status_code, request=httpx2.Request("GET", DEFAULT_URL)
        )
        return mocker.patch(
            "src.doc_analyzer_backend.api.routers.data_sources_router.upload_content_from_url",
            side_effect=httpx2.HTTPStatusError(
                message=error_message,
                request=mock_response.request,
                response=mock_response,
            ),
        )

    return _mock_upload_error


@pytest.fixture
def mock_upload_from_url_with_exception(mocker):
    """
    Function 'upload_content_from_url' mock with exception

    Returns:
        Function that setup mock with required exception class
    """

    def _mock_upload_exception(exception_class: type, exception_message: str) -> Mock:
        return mocker.patch(
            "src.doc_analyzer_backend.api.routers.data_sources_router.upload_content_from_url",
            side_effect=exception_class(exception_message),
        )

    return _mock_upload_exception
