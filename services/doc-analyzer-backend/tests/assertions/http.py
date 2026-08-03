import allure


def assert_response_success(
    response,
    expected_status_code: int,
    expected_header_name: str = "content-type",
    expected_header_value: str = "application/json",
) -> dict:
    with allure.step(f"Проверка статус-кода ответа ({expected_status_code})"):
        assert response.status_code == expected_status_code, (
            f"Status code expected {expected_status_code} but {response.status_code} received. "
            f"Response body: {response.text}"
        )

    with allure.step(
        f"Проверка заголовков ответа ({expected_header_name}: {expected_header_value})"
    ):
        assert response.headers[expected_header_name] == expected_header_value, (
            f"Expected header {expected_header_name}: {expected_header_value} "
            f"not found in received headers: {response.headers}."
        )

    with allure.step("Парсинг тела ответа"):
        return response.json()


def assert_response_fail(
    response,
    expected_status_code: int,
    error_field_name: str = "detail",
    expected_error_message_part: str | None = None,
) -> dict:
    with allure.step(f"Проверка статус-кода ответа ({expected_status_code})"):
        assert response.status_code == expected_status_code, (
            f"Status code expected {expected_status_code} but {response.status_code} received. "
            f"Response body: {response.text}"
        )

    with allure.step("Проверка структуры тела ошибки"):
        data = response.json()
        assert error_field_name in data, (
            f"No '{error_field_name}' field in error response body: {response.text}"
        )
        if expected_error_message_part:
            if error_field_name == "detail":
                assert any(
                    expected_error_message_part in str(field.get("msg", []))
                    for field in data[error_field_name]
                ), (
                    f"Expected error message '{error_field_name}' containing '{expected_error_message_part}' "
                    f"not found in response body: {response.text}"
                )
            else:
                assert expected_error_message_part in data[error_field_name], (
                    f"Expected error message '{error_field_name}' containing '{expected_error_message_part}' "
                    f"not found in response body: {response.text}"
                )

        return data
