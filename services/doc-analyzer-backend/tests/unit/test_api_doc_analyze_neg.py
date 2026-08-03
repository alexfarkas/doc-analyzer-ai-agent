import allure
import pytest

from tests.assertions.http import assert_response_fail
from tests.factories.payloads.invalid import (
    make_doc_analyze_payload_without_mandatory_resources,
    make_doc_analyze_payload_without_mandatory_role,
    make_doc_analyze_payload_without_mandatory_agents,
    make_doc_analyze_payload_with_invalid_role,
    make_doc_analyze_payload_with_empty_agents,
    make_doc_analyze_payload_with_invalid_assignment,
)
from tests.factories.payloads.valid import make_doc_analyze_payload

ANALYZE_DOC_PATH = "/doc/analyze"


@allure.epic("Documents Analyzer AI Agent API")
@allure.feature(f"Анализ документов ИИ-агентом {ANALYZE_DOC_PATH}")
class TestApiDocAnalyzeNegative:
    @allure.title(
        "Ошибка 422 при попытке анализа документа без передачи обязательных полей"
    )
    @allure.description(
        f"Запрос POST {ANALYZE_DOC_PATH} возвращает 422, если не передано обязательное поле."
    )
    @pytest.mark.parametrize(
        "payload",
        [
            pytest.param(
                make_doc_analyze_payload_without_mandatory_resources(),
                id="without_resources",
            ),
            pytest.param(
                make_doc_analyze_payload_without_mandatory_role(),
                id="without_role",
            ),
            pytest.param(
                make_doc_analyze_payload_without_mandatory_agents(),
                id="empty_agents",
            ),
        ],
    )
    def test_post_doc_analyze_no_mandatory_field_fail(
        self, test_api_client, mock_agent, payload
    ):
        with allure.step(f"Выполнение запроса POST {ANALYZE_DOC_PATH}"):
            response = test_api_client.post(ANALYZE_DOC_PATH, json=payload)

        assert_response_fail(response=response, expected_status_code=422)

        with allure.step("Проверка, что агент не вызывался"):
            mock_agent.analyze_doc.assert_not_called()

    @allure.title(
        "Ошибка 422 при попытке анализа документа с передачей невалидного значения обязательного поля"
    )
    @allure.description(
        f"Запрос POST {ANALYZE_DOC_PATH} возвращает 422, "
        "если передано невалидное значения обязательного поля."
    )
    @pytest.mark.parametrize(
        "payload",
        [
            pytest.param(
                make_doc_analyze_payload_with_invalid_role(),
                id="invalid_role",
            ),
            pytest.param(
                make_doc_analyze_payload_with_empty_agents(),
                id="empty_agents",
            ),
            pytest.param(
                make_doc_analyze_payload_with_invalid_assignment(),
                id="invalid_assignment",
            ),
        ],
    )
    def test_post_doc_analyze_invalid_field_value_fail(
        self, test_api_client, mock_agent, payload
    ):
        with allure.step(f"Выполнение запроса POST {ANALYZE_DOC_PATH}"):
            response = test_api_client.post(ANALYZE_DOC_PATH, json=payload)

        assert_response_fail(response=response, expected_status_code=422)

        with allure.step("Проверка, что агент не вызывался"):
            mock_agent.analyze_doc.assert_not_called()

    @allure.title("Ошибка 500, если в агент выбросил исключение")
    @allure.description(
        f"Запрос POST {ANALYZE_DOC_PATH} возвращает 500, если агент выбросил исключение."
    )
    def test_post_doc_analyze_agent_exception_fail(
        self, test_api_client, failing_mock_agent
    ):
        with allure.step("Подготовка тестовых данных"):
            payload = make_doc_analyze_payload()

        with allure.step(f"Выполнение запроса POST {ANALYZE_DOC_PATH}"):
            response = test_api_client.post(ANALYZE_DOC_PATH, json=payload)

        assert_response_fail(
            response=response,
            expected_status_code=500,
            error_field_name="message",
            expected_error_message_part="Unhandled exception",
        )
