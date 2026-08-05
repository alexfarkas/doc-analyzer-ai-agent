import allure
import pytest

from src.doc_analyzer_backend.config.loader.settings import app_settings
from tests.assertions.http import assert_response_success
from tests.assertions.uploads import assert_upload_response_body
from tests.consts.files import (
    DEFAULT_FILENAME_WO_EXT,
    DEFAULT_FILE_PATH,
    DEFAULT_FILE_EXT,
    LONG_FILENAME_LENGTH,
    LARGE_FILE_SIZE,
    DEFAULT_FILENAME_WITH_EXT,
)
from tests.factories.payloads.valid import make_file_payload

UPLOAD_FILE_PATH = "/upload/file"

SUPPORTED_EXTS = app_settings().app.allowed_exts


@allure.epic("Documents Analyzer AI Agent API")
@allure.feature(f"Загрузка файлов {UPLOAD_FILE_PATH}")
class TestApiUploadFilePositive:
    @allure.title("Загрузка файла с поддерживаемым расширением")
    @allure.description(
        f"Запрос POST {UPLOAD_FILE_PATH} возвращает 200 OK и корректное тело ответа "
        "после загрузки файла с поддерживаемым расширением."
    )
    @pytest.mark.parametrize(
        "ext",
        [pytest.param(ext, id=ext) for ext in SUPPORTED_EXTS],
    )
    def test_post_upload_file_supported_extension_success(
        self, test_api_client, mock_upload_file, ext
    ):
        with allure.step("Подготовка тестовых данных"):
            filename = f"{DEFAULT_FILENAME_WO_EXT}{ext}"
            file_path = f"{DEFAULT_FILE_PATH}/{filename}"

            file = make_file_payload(filename=filename)
            mock_upload_file(filename=filename)

        with allure.step(f"Выполнение запроса POST {UPLOAD_FILE_PATH}"):
            response = test_api_client.post(UPLOAD_FILE_PATH, files=file)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_upload_response_body(
            data=data, expected_path=file_path, expected_filename=filename
        )

    @allure.title("Загрузка файла с корректным именем")
    @allure.description(
        f"Запрос POST {UPLOAD_FILE_PATH} возвращает 200 OK и корректное тело ответа "
        "после загрузки файла с корректным именем, включая пробелы, цифры, кириллицу, спецсимволы."
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
    def test_post_upload_file_valid_filename_success(
        self, test_api_client, mock_upload_file, name
    ):
        with allure.step("Подготовка тестовых данных"):
            filename = f"{name}.{DEFAULT_FILE_EXT}"
            file_path = f"{DEFAULT_FILE_PATH}/{filename}"

            file = make_file_payload(filename=filename)
            mock_upload_file(filename=filename)

        with allure.step(f"Выполнение запроса POST {UPLOAD_FILE_PATH}"):
            response = test_api_client.post(UPLOAD_FILE_PATH, files=file)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_upload_response_body(
            data=data, expected_path=file_path, expected_filename=filename
        )

    @allure.title("Загрузка файла с длинным именем")
    @allure.description(
        f"Запрос POST {UPLOAD_FILE_PATH} возвращает 200 OK и корректное тело ответа "
        "после загрузки файла с длинными именем."
    )
    def test_post_upload_file_long_filename_success(
        self, test_api_client, mock_upload_file
    ):
        with allure.step("Подготовка тестовых данных"):
            long_filename = f"{'a' * LONG_FILENAME_LENGTH}.{DEFAULT_FILE_EXT}"
            file_path = f"{DEFAULT_FILE_PATH}/{long_filename}"

            file = make_file_payload(filename=long_filename)
            mock_upload_file(filename=long_filename)

        with allure.step(f"Выполнение запроса POST {UPLOAD_FILE_PATH}"):
            response = test_api_client.post(UPLOAD_FILE_PATH, files=file)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_upload_response_body(
            data=data, expected_path=file_path, expected_filename=long_filename
        )

    @allure.title("Загрузка файла большого размера")
    @allure.description(
        f"Запрос POST {UPLOAD_FILE_PATH} возвращает 200 OK и корректное тело ответа "
        "после загрузки файла большого размера."
    )
    def test_post_upload_file_large_content_success(
        self, test_api_client, mock_upload_file
    ):
        with allure.step("Подготовка тестовых данных"):
            filename = "large_file.txt"
            file_path = f"{DEFAULT_FILE_PATH}/{filename}"
            large_content = b"x" * LARGE_FILE_SIZE

            file = make_file_payload(filename=filename, content=large_content)
            mock_upload_file(filename=filename)

        with allure.step(f"Выполнение запроса POST {UPLOAD_FILE_PATH}"):
            response = test_api_client.post(UPLOAD_FILE_PATH, files=file)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_upload_response_body(
            data=data, expected_path=file_path, expected_filename=filename
        )

    @allure.title("Повторная загрузка файла с тем же именем")
    @allure.description(
        f"Оба запроса POST {UPLOAD_FILE_PATH} возвращают 200 OK и корректные тела ответов "
        "после повторной загрузки файла с тем же именем."
    )
    def test_post_upload_file_duplicate_success(
        self, test_api_client, mock_upload_file
    ):
        with allure.step("Подготовка тестовых данных"):
            filename = DEFAULT_FILENAME_WITH_EXT
            file_path = f"{DEFAULT_FILE_PATH}/{filename}"

            file1 = make_file_payload(filename=filename, content=b"first content")
            file2 = make_file_payload(filename=filename, content=b"second content")

            mock_upload_file(filename=filename)

        with allure.step(f"Первое выполнение запроса POST {UPLOAD_FILE_PATH}"):
            response1 = test_api_client.post(UPLOAD_FILE_PATH, files=file1)

        data1 = assert_response_success(response=response1, expected_status_code=200)

        with allure.step(
            f"Выполнение запроса POST {UPLOAD_FILE_PATH} с тем же именем файла"
        ):
            response2 = test_api_client.post(UPLOAD_FILE_PATH, files=file2)

        data2 = assert_response_success(response=response2, expected_status_code=200)

        with allure.step("Проверка тела ответа загрузки файлов"):
            assert data1["file_path"] == data2["file_path"] == file_path
            assert data1["filename"] == data2["filename"] == filename
