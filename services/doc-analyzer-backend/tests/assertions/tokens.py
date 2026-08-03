import allure


def assert_consumption_data(data: dict, expected: dict):
    with allure.step("Проверка token_usage"):
        assert data["token_usage"] == expected["token_usage"]

    with allure.step("Проверка elapsed"):
        assert data["elapsed"] == expected["elapsed"]

    with allure.step("Проверка cost"):
        assert data["cost"] == expected["cost"]


def assert_total_token_usage_exists(data: dict):
    with allure.step("Проверка наличия total_token_usage"):
        assert "total_token_usage" in data
        assert data["total_token_usage"] is not None
