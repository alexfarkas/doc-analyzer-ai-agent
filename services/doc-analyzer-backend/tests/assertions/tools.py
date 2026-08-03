import allure


def assert_tools_data(data: dict, expected_tools: list[tuple[str, str]]):
    """Check tools in GET /status response. Description is cut by new line."""
    with allure.step("Проверка информации о тулах в ответе статуса"):
        assert data["tools"] == [
            {"name": n, "description": d.split("\n")[0]} for n, d in expected_tools
        ]
