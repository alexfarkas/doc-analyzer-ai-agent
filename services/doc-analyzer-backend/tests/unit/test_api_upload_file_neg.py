import allure

from tests.assertions.http import assert_response_fail
from tests.consts.files import DEFAULT_FILENAME_WO_EXT
from tests.factories.payloads.valid import make_file_payload

UPLOAD_FILE_PATH = "/upload/file"

UNSUPPORTED_EXT = ".exe"


@allure.epic("Documents Analyzer AI Agent API")
@allure.feature(f"Загрузка файлов {UPLOAD_FILE_PATH}")
class TestApiUploadFileNegative:
    @allure.title("Неподдерживаемый формат загружаемого файла")
    @allure.description(
        f"Запрос POST {UPLOAD_FILE_PATH} возвращает 400 "
        "при попытке загрузки файла с неподдердживаемым расширением."
    )
    def test_post_upload_file_unsupported_extension_fail(
        self, test_api_client, mock_file_system
    ):
        with allure.step("Подготовка тестовых данных"):
            filename = f"{DEFAULT_FILENAME_WO_EXT}{UNSUPPORTED_EXT}"
            file = make_file_payload(filename=filename)

        with allure.step(f"Выполнение запроса POST {UPLOAD_FILE_PATH}"):
            response = test_api_client.post(UPLOAD_FILE_PATH, files=file)

        assert_response_fail(
            response=response,
            expected_status_code=400,
            error_field_name="message",
            expected_error_message_part="extension not supported",
        )

    @allure.title("Отсутствует расширение у загружаемого файла")
    @allure.description(
        f"Запрос POST {UPLOAD_FILE_PATH} возвращает 400 "
        "при попытке загрузки файла без расширения."
    )
    def test_post_upload_file_no_extension_fail(
        self, test_api_client, mock_file_system
    ):
        with allure.step("Подготовка тестовых данных"):
            filename = DEFAULT_FILENAME_WO_EXT
            file = make_file_payload(filename=filename)

        with allure.step(f"Выполнение запроса POST {UPLOAD_FILE_PATH}"):
            response = test_api_client.post(UPLOAD_FILE_PATH, files=file)

        assert_response_fail(
            response=response,
            expected_status_code=400,
            error_field_name="message",
            expected_error_message_part="extension not supported",
        )

    @allure.title("Отсутствует файл в запросе на загрузку")
    @allure.description(
        f"Запрос POST {UPLOAD_FILE_PATH} возвращает 422 "
        "если в запросе на загрузку отсутствует файл."
    )
    def test_post_upload_file_no_file_in_request_fail(self, test_api_client):
        with allure.step(f"Выполнение запроса POST {UPLOAD_FILE_PATH}"):
            response = test_api_client.post(UPLOAD_FILE_PATH)

        assert_response_fail(response=response, expected_status_code=422)

    @allure.title("Пустое имя загружаемого файла")
    @allure.description(
        f"Запрос POST {UPLOAD_FILE_PATH} возвращает 422 "
        "при попытке загрузки файла с пустым именем."
    )
    def test_post_upload_file_empty_filename_fail(
        self, test_api_client, mock_file_system
    ):
        with allure.step("Подготовка тестовых данных"):
            empty_filename = ""
            file = make_file_payload(filename=empty_filename)

        with allure.step(f"Выполнение запроса POST {UPLOAD_FILE_PATH}"):
            response = test_api_client.post(UPLOAD_FILE_PATH, files=file)

        assert_response_fail(response=response, expected_status_code=422)
