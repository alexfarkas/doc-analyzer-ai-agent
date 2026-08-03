import allure
import pytest

from tests.assertions.http import assert_response_success
from tests.assertions.tokens import assert_consumption_data, assert_total_token_usage_exists
from tests.factories.payloads.valid import (
    make_doc_analyze_payload,
    make_council_doc_analyze_payload,
)
from tests.factories.responses import (
    make_expected_agent_analyze_doc_response,
    make_expected_council_analyze_doc_response,
)

ANALYZE_DOC_PATH = "/doc/analyze"

MANY_RESOURCES_COUNT = 100


@allure.epic("Documents Analyzer AI Agent API")
@allure.feature(f"Анализ документов ИИ-агентом {ANALYZE_DOC_PATH}")
class TestApiDocAnalyzePositive:
    @allure.title("Анализ документов одним агентом")
    @allure.description(
        f"Запрос POST {ANALYZE_DOC_PATH} возвращает 200 OK и корректное тело ответа "
        "при использовании одного агента для разного набора анализируемых ресурсов."
    )
    @pytest.mark.parametrize(
        "resources, expected_call_count",
        [
            pytest.param([], 0, id="empty resources"),
            pytest.param(["/app/documents/test.txt"], 1, id="single_resource_file"),
            pytest.param(
                ["/app/documents/test_1.txt", "/app/documents/test_2.docs"],
                2,
                id="multiple_resources_files",
            ),
            pytest.param(["https://example.com"], 1, id="single_resource_url"),
            pytest.param(
                ["https://example_1.com", "https://example_2.com"],
                2,
                id="multiple_resources_urls",
            ),
        ],
    )
    def test_post_doc_analyze_single_agent_success(
        self,
        test_api_client,
        mock_agent,
        resources: list[str],
        expected_call_count: int,
    ):
        with allure.step("Подготовка тестовых данных"):
            payload = make_doc_analyze_payload(resources=resources)
            expected_data = make_expected_agent_analyze_doc_response()

        with allure.step(f"Выполнение запроса POST {ANALYZE_DOC_PATH}"):
            response = test_api_client.post(ANALYZE_DOC_PATH, json=payload)

        data = assert_response_success(response=response, expected_status_code=200)

        with allure.step("Проверка тела ответа"):
            assert data["result"] == expected_data["result"]
            assert_consumption_data(data, expected_data["consumption_data"])
            assert_total_token_usage_exists(data=data)

        with allure.step("Проверка вызова агента"):
            mock_agent.analyze_doc.assert_called_once_with(
                resources=resources,
                role=payload["role"],
                model=payload["agents"][0]["model"],
            )

    @allure.title("Анализ документов несколькими агентами (совет агентов)")
    @allure.description(
        f"Запрос POST {ANALYZE_DOC_PATH} возвращает 200 OK и корректное тело ответа "
        "при использовании нескольких агентов для разного набора ресурсов."
    )
    def test_post_doc_analyze_council_success(self, test_api_client, mock_council):
        with allure.step("Подготовка тестовых данных"):
            payload = make_council_doc_analyze_payload()
            expected_data = make_expected_council_analyze_doc_response()

        with allure.step(f"Выполнение запроса POST {ANALYZE_DOC_PATH}"):
            response = test_api_client.post(ANALYZE_DOC_PATH, json=payload)

        data = assert_response_success(response=response, expected_status_code=200)

        with allure.step("Проверка тела ответа"):
            assert data["result"] == expected_data["result"]
            assert_consumption_data(data, expected_data["consumption_data"])
            assert_total_token_usage_exists(data=data)

        with allure.step(
            'Проверка вызова функции "create_council" с корректными параметрами'
        ):
            mock_council.create_council.assert_called_once()

        with allure.step("Проверка вызова агента"):
            mock_council.analyze_doc.assert_called_once_with(
                resources=payload["resources"], role=payload["role"]
            )

    @allure.title("Анализ большого количества документов")
    @allure.description(
        f"Запрос POST {ANALYZE_DOC_PATH} возвращает 200 OK и корректно вызывает агента "
        f"при анализе большого количества документов."
    )
    def test_post_doc_analyze_many_resources_success(self, test_api_client, mock_agent):
        with allure.step("Подготовка тестовых данных"):
            payload = make_doc_analyze_payload(
                resources=[
                    f"/app/documents/test_{i}.txt" for i in range(MANY_RESOURCES_COUNT)
                ],
            )

        with allure.step(f"Выполнение запроса POST {ANALYZE_DOC_PATH}"):
            response = test_api_client.post(ANALYZE_DOC_PATH, json=payload)

        assert_response_success(response=response, expected_status_code=200)

        with allure.step("Проверка вызова агента"):
            mock_agent.analyze_doc.assert_called_once()
            call_args = mock_agent.analyze_doc.call_args
            assert len(call_args.kwargs["resources"]) == MANY_RESOURCES_COUNT
