import allure

from tests.assertions.http import assert_response_success
from tests.consts.health import (
    EXPECTED_HEALTH_CHECK_SUCCESS,
    EXPECTED_HEALTH_CHECK_FAIL,
)
from tests.consts.llm import DEFAULT_LLM_MODEL

HEALTH_CHECK_PATH = "/health"


@allure.epic("Documents Analyzer AI Agent API")
@allure.feature(f"Health-check сервиса {HEALTH_CHECK_PATH}")
class TestApiHealthCheck:
    @allure.title("Запрос health-check c инициализированным агентом")
    @allure.description(
        f"Запрос GET {HEALTH_CHECK_PATH} с инициализированным агентом возвращает 200 OK "
        'и сообщение со статусом "OK" и названием LLM-модели.'
    )
    def test_health_check_success(self, test_api_client, mock_llm_config):
        with allure.step("Выполнение запроса GET /status"):
            response = test_api_client.get(HEALTH_CHECK_PATH)

        data = assert_response_success(response=response, expected_status_code=200)

        with allure.step("Проверка тела ответа"):
            assert data["status"] == EXPECTED_HEALTH_CHECK_SUCCESS
            assert data["model"] == DEFAULT_LLM_MODEL

    @allure.title("Запрос health-check без инициализированного агента")
    @allure.description(
        "Запрос GET /health без инициализированного агента возвращает 200 OK "
        'и сообщение "Agent is not initialized".'
    )
    def test_health_check_agent_not_initialized_success(self, test_api_client_no_agent):
        with allure.step("Выполнение запроса GET /status"):
            response = test_api_client_no_agent.get(HEALTH_CHECK_PATH)

        data = assert_response_success(response=response, expected_status_code=200)

        with allure.step("Проверка тела ответа"):
            assert data["status"] == EXPECTED_HEALTH_CHECK_FAIL
