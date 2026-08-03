import allure
import pytest

from src.doc_analyzer_backend.api.exceptions.exceptions import (
    AgentFileNotFoundError,
    AgentUnsupportedFileExtensionError,
    AgentFilePreviewError,
    AgentDirectoryInsteadOfFileError,
)
from tests.assertions.http import assert_response_fail
from tests.factories.payloads.valid import make_preview_params

FILES_PREVIEW_PATH = "/files/preview"


@allure.epic("Documents Analyzer AI Agent API")
@allure.feature(f"Получение превью файлов {FILES_PREVIEW_PATH}")
class TestApiFilesPreviewNegative:
    @allure.title("Файл для превью не найден")
    @allure.description(
        f"Запрос GET {FILES_PREVIEW_PATH} возвращает 404, "
        f"если файл для превью не найден."
    )
    @pytest.mark.parametrize(
        "error_class, status_code, error_message",
        [
            pytest.param(
                AgentUnsupportedFileExtensionError,
                400,
                "extension not supported",
                id="extension_not_supported",
            ),
            pytest.param(
                AgentFileNotFoundError,
                404,
                "File not found",
                id="file_not_found",
            ),
            pytest.param(
                AgentFilePreviewError,
                500,
                "preview error",
                id="file_read_error",
            ),
            pytest.param(
                AgentDirectoryInsteadOfFileError,
                400,
                "File expected but directory received",
                id="directory_instead_of_file",
            ),
        ],
    )
    def test_get_file_preview_file_not_found_fail(
        self,
        test_api_client,
        mock_preview_with_error,
        error_class,
        status_code,
        error_message,
    ):
        with allure.step("Подготовка тестовых данных"):
            params = make_preview_params()
            mock_preview_with_error(error_class=error_class)

        with allure.step(f"Выполнение запроса GET {FILES_PREVIEW_PATH}"):
            response = test_api_client.get(FILES_PREVIEW_PATH, params=params)

        assert_response_fail(
            response=response,
            expected_status_code=status_code,
            error_field_name="message",
            expected_error_message_part=error_message,
        )

    @allure.title("Файл для превью превышает допустимый размер")
    @allure.description(
        f"Запрос GET {FILES_PREVIEW_PATH} возвращает 413, "
        "если файл для превью превышает допустимый размер."
    )
    def test_get_file_preview_too_large_content_fail(
        self, test_api_client, mock_preview_with_file_too_large_error
    ):
        with allure.step("Подготовка тестовых данных"):
            params = make_preview_params()
            mock_preview_with_file_too_large_error()

        with allure.step(f"Выполнение запроса GET {FILES_PREVIEW_PATH}"):
            response = test_api_client.get(FILES_PREVIEW_PATH, params=params)

        assert_response_fail(
            response=response,
            expected_status_code=413,
            error_field_name="message",
            expected_error_message_part="too large for preview",
        )

    @allure.title("Отсутствует путь к файлу в запросе превью")
    @allure.description(
        f"Запрос GET {FILES_PREVIEW_PATH} возвращает 422, "
        "если в запросе на превью отсутствует путь к файлу."
    )
    def test_get_file_preview_no_filepath_fail(self, test_api_client):
        with allure.step(f"Выполнение запроса GET {FILES_PREVIEW_PATH}"):
            response = test_api_client.get(FILES_PREVIEW_PATH)

        assert_response_fail(response=response, expected_status_code=422)
