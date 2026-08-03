import allure
import pytest

from tests.assertions.http import assert_response_success
from tests.assertions.uploads import assert_upload_from_url_response_body
from tests.consts.urls import DEFAULT_WEB_CONTENT, DEFAULT_URL, LARGE_WEB_CONTENT_LENGTH
from tests.factories.payloads.valid import make_url_payload
from tests.utils.url_normalizer import normalize_url

UPLOAD_FROM_URL_PATH = "/upload/from-url"


@allure.epic("Documents Analyzer AI Agent API")
@allure.feature(f"Загрузка данных по URL {UPLOAD_FROM_URL_PATH}")
class TestApiUploadFromUrlPositive:
    @allure.title("Загрузка данных по валидному URL")
    @allure.description(
        f"Запрос POST {UPLOAD_FROM_URL_PATH} возвращает 200 OK и корректное тело ответа "
        "после загрузки данных по различным корректным URL с различным контентом."
    )
    @pytest.mark.parametrize(
        "url, html",
        [
            pytest.param(
                "https://example.com/article",
                "<html><body><h1>Test Article</h1></body></html>",
                id="url_wo_params_latin_content",
            ),
            pytest.param(
                "https://example.com/search?q=test&page=1",
                "<html><body><h1>Search Result</h1></body></html>",
                id="url_with_params_latin_content",
            ),
            pytest.param(
                "https://пример.рф/статья",
                "<html><body><h1>Кириллический Контент</h1></body></html>",
                id="url_wo_params_cyrillic_content",
            ),
        ],
    )
    def test_post_upload_from_url_success(
        self, test_api_client, mock_upload_from_url, url, html
    ):
        with allure.step("Подготовка тестовых данных"):
            mock_upload = mock_upload_from_url(html)
            payload = make_url_payload(url=url)

        with allure.step(f"Выполнение запроса POST {UPLOAD_FROM_URL_PATH}"):
            response = test_api_client.post(UPLOAD_FROM_URL_PATH, json=payload)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_upload_from_url_response_body(
            data=data,
            expected_url=url,
            expected_html=html,
        )

        with allure.step("Проверка вызова агента"):
            mock_upload.assert_called_once_with(normalize_url(url))

    @allure.title("Загрузка большого объема данных по URL")
    @allure.description(
        f"Запрос POST {UPLOAD_FROM_URL_PATH} возвращает 200 OK и корректное тело ответа "
        "после загрузки большого объема данных по URL."
    )
    def test_post_upload_from_url_large_content_success(
        self, test_api_client, mock_upload_from_url
    ):
        with allure.step("Подготовка тестовых данных"):
            html = DEFAULT_WEB_CONTENT.format(
                placeholder="x" * LARGE_WEB_CONTENT_LENGTH
            )

            mock_upload = mock_upload_from_url(html)
            payload = make_url_payload()

        with allure.step(f"Выполнение запроса POST {UPLOAD_FROM_URL_PATH}"):
            response = test_api_client.post(UPLOAD_FROM_URL_PATH, json=payload)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_upload_from_url_response_body(
            data=data,
            expected_url=DEFAULT_URL,
            expected_html=html,
        )

        with allure.step("Проверка вызова агента"):
            mock_upload.assert_called_once_with(DEFAULT_URL)
