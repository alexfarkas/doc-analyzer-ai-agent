import allure

from src.doc_analyzer_backend.utils.truncate import truncate_value


def assert_file_review_response_body(data: dict, expected_data: dict):
    with allure.step("Проверка тела ответа превью файла"):
        for field in ["status", "filename", "format", "metadata", "blocks"]:
            assert field in data, (
                f"No '{field}' field in preview response: {truncate_value(value=data, max_length=20)}"
            )

            assert data[field] == expected_data[field], (
                f"Expected {field} '{expected_data[field]}' "
                f"but found '{data[field]}' in preview response: {truncate_value(value=data, max_length=20)}"
            )
