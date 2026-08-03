import allure
import pytest

from tests.assertions.http import assert_response_success
from tests.assertions.tools import assert_tools_data
from tests.consts.llm import DEFAULT_LLM_MODEL, DEFAULT_LLM_TEMPERATURE
from tests.consts.rag import (
    DEFAULT_RAG_MODEL,
    DEFAULT_RAG_TOP_K,
    DEFAULT_RAG_SIMILARITY_THRESHOLD,
)
from tests.factories.mocks import make_tool_mock

STATUS_PATH = "/status"


@allure.epic("Documents Analyzer AI Agent API")
@allure.feature(f"Статус сервиса {STATUS_PATH}")
class TestApiStatus:
    @allure.title("Получение статуса с разными тулами LLM без RAG")
    @allure.description(
        f"Запрос GET {STATUS_PATH} с разными тулами LLM без RAG возвращает 200 OK"
        " и корректное тело ответа."
    )
    @pytest.mark.parametrize(
        "tools",
        [
            pytest.param([], id="without_tools"),
            pytest.param(
                [("single tool name", "single tool description")], id="single_tool"
            ),
            pytest.param(
                [("tool name", "first line\nsecond line\nthird line")],
                id="multi_line_tool_description",
            ),
            pytest.param(
                [
                    ("tool name 1", "tool description 1"),
                    ("tool name 2", "tool description 2"),
                ],
                id="several_tools",
            ),
        ],
    )
    def test_status_llm_tools_no_rag_success(
        self, test_api_client, mock_agent, mock_llm_config, mock_rag_config, tools
    ):
        with allure.step("Подготовка тестовых данных"):
            mock_rag_config.use_vector_db = False
            mock_agent.tools = [make_tool_mock(n, d) for n, d in tools]

        with allure.step(f"Выполнение запроса GET {STATUS_PATH}"):
            response = test_api_client.get(STATUS_PATH)

        data = assert_response_success(response, 200)

        with allure.step("Проверка тела ответа"):
            assert data["model"] == DEFAULT_LLM_MODEL
            assert data["temperature"] == DEFAULT_LLM_TEMPERATURE
            assert data["use_rag"] is False
            assert_tools_data(data, tools)

            assert "rag" not in data
            assert data.get("rag") is None

    @allure.title("Получение статуса с данными RAG")
    @allure.description(
        f"Запрос GET {STATUS_PATH} с данными RAG возвращает 200 OK и корректное тело ответа, "
        "в котором есть блок с информаицей о RAG."
    )
    def test_status_with_rag_success(
        self, test_api_client, mock_agent, mock_llm_config, mock_rag_config
    ):
        with allure.step("Подготовка тестовых данных"):
            mock_rag_config.use_vector_db = True
            mock_agent.tools = []

        with allure.step(f"Выполнение запроса GET {STATUS_PATH}"):
            response = test_api_client.get(STATUS_PATH)

        data = assert_response_success(response=response, expected_status_code=200)

        with allure.step("Проверка тела ответа"):
            assert data["model"] == DEFAULT_LLM_MODEL
            assert data["temperature"] == DEFAULT_LLM_TEMPERATURE
            assert data["tools"] == []
            assert data["use_rag"] is True

            assert data["rag"]["model"] == DEFAULT_RAG_MODEL
            assert data["rag"]["top_k"] == DEFAULT_RAG_TOP_K
            assert (
                data["rag"]["similarity_threshold"] == DEFAULT_RAG_SIMILARITY_THRESHOLD
            )
