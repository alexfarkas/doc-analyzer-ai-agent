import allure
import httpx2
import pytest

from tests.assertions.http import assert_response_fail
from tests.factories.payloads.valid import make_url_payload

UPLOAD_FROM_URL_PATH = "/upload/from-url"


@allure.epic("Documents Analyzer AI Agent API")
@allure.feature(f"Загрузка данных по URL {UPLOAD_FROM_URL_PATH}")
class TestApiUploadFromUrlNegative:
    @allure.title("Невалидный URL в запросе на загрузку")
    @allure.description(
        f"Запрос POST {UPLOAD_FROM_URL_PATH} возвращает 422 "
        "при невалидном URL в запросе."
    )
    @pytest.mark.parametrize(
        "payload, error_message",
        [
            pytest.param(
                make_url_payload(url="example.com/article"),
                "Input should be a valid URL",
                id="url_without_scheme",
            ),
            pytest.param(
                make_url_payload(url="not url"),
                "Input should be a valid URL",
                id="invalid_url_format",
            ),
            pytest.param(
                make_url_payload(url="ftp://example.com/file"),
                "URL scheme should be 'http' or 'https'",
                id="unsupported_protocol",
            ),
            pytest.param(
                make_url_payload(url=""),
                "Input should be a valid URL",
                id="empty_url",
            ),
            pytest.param(
                "http://example.com/article",
                "Input should be a valid dictionary or object to extract fields from",
                id="invalid_data_structure",
            ),
            pytest.param(
                {},
                "Field required",
                id="no_data",
            ),
        ],
    )
    def test_post_upload_from_url_invalid_url_fail(
        self, test_api_client, payload, error_message
    ):
        with allure.step(f"Выполнение запроса POST {UPLOAD_FROM_URL_PATH}"):
            response = test_api_client.post(UPLOAD_FROM_URL_PATH, json=payload)

        assert_response_fail(
            response=response,
            expected_status_code=422,
            expected_error_message_part=error_message,
        )

    @allure.title("Ошибка, если запрос ресурса возвращает HTTP-ошибку")
    @allure.description(
        f"Запрос POST {UPLOAD_FROM_URL_PATH} возвращает HTTP-ошибку, "
        "если при попытке запроса к URL возвращается статус-код с HTTP-ошибкой."
    )
    @pytest.mark.parametrize(
        "status_code, error_message",
        [
            pytest.param(404, "Not Found", id="status_code_404_not_found"),
            pytest.param(
                500, "Internal Server Error", id="status_code_500_internal_server_error"
            ),
        ],
    )
    def test_post_upload_from_url_http_error_fail(
        self,
        test_api_client,
        mock_upload_from_url_with_http_error,
        status_code,
        error_message,
    ):
        with allure.step("Подготовка тестовых данных"):
            mock_upload_from_url_with_http_error(
                status_code=status_code,
                error_message=error_message,
            )
            payload = make_url_payload()

        with allure.step(f"Выполнение запроса POST {UPLOAD_FROM_URL_PATH}"):
            response = test_api_client.post(UPLOAD_FROM_URL_PATH, json=payload)

        assert_response_fail(
            response=response,
            expected_status_code=500,
            error_field_name="message",
            expected_error_message_part="Unhandled exception",
        )

    @allure.title(
        "Ошибка при сетевых проблемах или исключениях при попытке запроса к URL"
    )
    @allure.description(
        f"Запрос POST {UPLOAD_FROM_URL_PATH} возвращает 500, "
        "если при попытке запроса к URL происходит сетевая ошибка или выбрасывается исключение."
    )
    @pytest.mark.parametrize(
        "exception_class, exception_message",
        [
            pytest.param(
                httpx2.TimeoutException,
                "Connection timed out",
                id="connection_timeout_exception",
            ),
            pytest.param(
                httpx2.ConnectError,
                "Could not connect",
                id="connect_error",
            ),
            pytest.param(
                Exception,
                "Unknown error",
                id="exception",
            ),
        ],
    )
    def test_post_upload_from_url_bad_connect_fail(
        self,
        test_api_client,
        mock_upload_from_url_with_exception,
        exception_class,
        exception_message,
    ):
        with allure.step("Подготовка тестовых данных"):
            mock_upload_from_url_with_exception(
                exception_class=exception_class, exception_message=exception_message
            )
            payload = make_url_payload()

        with allure.step(f"Выполнение запроса POST {UPLOAD_FROM_URL_PATH}"):
            response = test_api_client.post(UPLOAD_FROM_URL_PATH, json=payload)

        assert_response_fail(
            response=response,
            expected_status_code=500,
            error_field_name="message",
            expected_error_message_part="Unhandled exception",
        )
