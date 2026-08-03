import allure
import pytest

from src.doc_analyzer_backend.config.app_config import app_config
from tests.assertions.http import assert_response_success
from tests.assertions.preview import assert_file_review_response_body
from tests.consts.preview import (
    DEFAULT_PREVIEW_FILENAME_WO_EXT,
    DEFAULT_PREVIEW_FILE_PATH,
    DEFAULT_PREVIEW_FILE_EXT,
    LONG_PREVIEW_FILENAME_LENGTH,
    MAX_PREVIEW_FILE_SIZE,
)
from tests.factories.payloads.valid import make_preview_params
from tests.factories.responses import make_expected_file_preview_response

FILES_PREVIEW_PATH = "/files/preview"

SUPPORTED_EXTS = app_config.allowed_exts


@allure.epic("Documents Analyzer AI Agent API")
@allure.feature(f"Получение превью файлов {FILES_PREVIEW_PATH}")
class TestApiFilesPreviewPositive:
    @allure.title("Чтение превью файла с поддерживаемым расширением")
    @allure.description(
        f"Запрос GET {FILES_PREVIEW_PATH} возвращает 200 OK и корректное тело ответа "
        "после получения превью файла с поддерживаемым расширением."
    )
    @pytest.mark.parametrize(
        "ext",
        [pytest.param(ext, id=ext) for ext in SUPPORTED_EXTS],
    )
    def test_get_file_preview_supported_extension_success(
        self, test_api_client, mock_file_preview, ext
    ):
        with allure.step("Подготовка тестовых данных"):
            filename = f"{DEFAULT_PREVIEW_FILENAME_WO_EXT}{ext}"
            file_path = f"{DEFAULT_PREVIEW_FILE_PATH}/{filename}"

            params = make_preview_params(file_path=file_path)

            expected_data = make_expected_file_preview_response(
                filename=filename, ext=ext
            )
            mock_file_preview(expected_data)

        with allure.step(f"Выполнение запроса GET {FILES_PREVIEW_PATH}"):
            response = test_api_client.get(FILES_PREVIEW_PATH, params=params)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_file_review_response_body(data=data, expected_data=expected_data)

    @allure.title("Чтение превью файла с корректным именем")
    @allure.description(
        f"Запрос GET {FILES_PREVIEW_PATH} возвращает 200 OK и корректное тело ответа "
        "после получения превью файла с корректным именем, "
        "включая проблемы, цифры, кириллицу спецсимволы."
    )
    @pytest.mark.parametrize(
        "name",
        [
            pytest.param("filename", id="single_latin_word"),
            pytest.param("Filename", id="latin_word_started_with_capital_letter"),
            pytest.param("fileName", id="latin_word_with_capital_letter_in_the_middle"),
            pytest.param("filename with spaces", id="latin_words_with_spaces"),
            pytest.param("filename1", id="latin_word_with_digit"),
            pytest.param("filename0001", id="latin_word_with_digits"),
            pytest.param(
                "filename#wiyj@specsymbols", id="latin_word_with_special_symbols"
            ),
            pytest.param("file_name", id="latin_word_with_underscore"),
            pytest.param("file-name", id="latin_word_with_dash"),
            pytest.param("file.name", id="latin_word_with_dot"),
            pytest.param("имяфайла", id="single_cyrillic_word"),
            pytest.param("Имяфайла", id="cyrillic_word_started_with_capital_letter"),
            pytest.param(
                "имяФайла", id="cyrillic_word_with_capital_letter_in_the_middle"
            ),
            pytest.param("имя.файла", id="cyrillic_word_with_dot"),
            pytest.param("имяфайла№1", id="cyrillic_word_with_special_symbols"),
        ],
    )
    def test_get_file_preview_valid_filename_success(
        self, test_api_client, mock_file_preview, name
    ):
        with allure.step("Подготовка тестовых данных"):
            filename = f"{name}.{DEFAULT_PREVIEW_FILE_EXT}"
            file_path = f"{DEFAULT_PREVIEW_FILE_PATH}/{filename}"

            params = make_preview_params(file_path=file_path)

            expected_data = make_expected_file_preview_response(
                filename=filename, ext=DEFAULT_PREVIEW_FILE_EXT
            )
            mock_file_preview(expected_data)

        with allure.step(f"Выполнение запроса GET {FILES_PREVIEW_PATH}"):
            response = test_api_client.get(FILES_PREVIEW_PATH, params=params)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_file_review_response_body(data=data, expected_data=expected_data)

    @allure.title("Чтение превью файла с длинным именем")
    @allure.description(
        f"Запрос GET {FILES_PREVIEW_PATH} возвращает 200 OK и корректное тело ответа "
        "после получения превью файла с длинным именем."
    )
    def test_get_file_preview_long_filename_success(
        self, test_api_client, mock_file_preview
    ):
        with allure.step("Подготовка тестовых данных"):
            long_filename = (
                f"{'a' * LONG_PREVIEW_FILENAME_LENGTH}.{DEFAULT_PREVIEW_FILE_EXT}"
            )
            file_path = f"{DEFAULT_PREVIEW_FILE_PATH}/{long_filename}"

            params = make_preview_params(file_path=file_path)

            expected_data = make_expected_file_preview_response(
                filename=long_filename, ext=DEFAULT_PREVIEW_FILE_EXT
            )
            mock_file_preview(expected_data)

        with allure.step(f"Выполнение запроса GET {FILES_PREVIEW_PATH}"):
            response = test_api_client.get(FILES_PREVIEW_PATH, params=params)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_file_review_response_body(data=data, expected_data=expected_data)

    @allure.title("Чтение превью файла допустимого размера")
    @allure.description(
        f"Запрос GET {FILES_PREVIEW_PATH} возвращает 200 OK и корректное тело ответа "
        "после получения превью файла допустимого размера."
    )
    @pytest.mark.parametrize(
        "file_size",
        [
            pytest.param(MAX_PREVIEW_FILE_SIZE / 2, id="file_size_half_max"),
            pytest.param(MAX_PREVIEW_FILE_SIZE - 1, id="file_size_max_min_1"),
            pytest.param(1, id="file_size_eq_1"),
            pytest.param(MAX_PREVIEW_FILE_SIZE, id="max_file_size"),
        ],
    )
    def test_get_file_preview_acceptable_file_size_success(
        self, test_api_client, mock_file_preview, file_size
    ):
        with allure.step("Подготовка тестовых данных"):
            params = make_preview_params(max_size=file_size)
            expected_data = make_expected_file_preview_response()

            mock_file_preview(expected_data)

        with allure.step(f"Выполнение запроса GET {FILES_PREVIEW_PATH}"):
            response = test_api_client.get(FILES_PREVIEW_PATH, params=params)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_file_review_response_body(data=data, expected_data=expected_data)
