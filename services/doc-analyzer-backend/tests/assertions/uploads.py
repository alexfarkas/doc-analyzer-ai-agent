import allure

from tests.utils.url_normalizer import normalize_url
from src.doc_analyzer_backend.utils.truncate import truncate_value


def assert_upload_response_body(
    data: dict,
    expected_path: str,
    expected_filename: str,
):
    with allure.step("Проверка тела ответа загрузки файла"):
        assert "file_path" in data, f"No 'file_path' field in upload response: {data}"
        assert "filename" in data, f"No 'filename' field in upload response: {data}"

        assert data["file_path"] == expected_path, (
            f"Expected upload path '{expected_path}' "
            f"but found '{data['file_path']}' in upload response: {data}"
        )
        assert data["filename"] == expected_filename, (
            f"Expected upload filename '{expected_filename}' "
            f"but found '{data['filename']}' in upload response: {data}"
        )


def assert_upload_from_url_response_body(
    data: dict,
    expected_url: str,
    expected_html: str,
):
    normalized_expected_url = normalize_url(expected_url)
    with allure.step("Проверка тела ответа загрузки по URL"):
        assert "url" in data, (
            f"No 'url' field in upload response: {truncate_value(value=data, max_length=20)}"
        )
        assert "html" in data, (
            f"No 'html' field in upload response: {truncate_value(value=data, max_length=20)}"
        )

        assert data["url"] == normalized_expected_url, (
            f"Expected URL '{normalized_expected_url[:20]}' "
            f"but found '{truncate_value(value=data['url'], max_length=20)}' "
            f"in upload response: {truncate_value(value=data, max_length=20)}"
        )
        assert data["html"] == expected_html, (
            f"Expected upload path '{expected_html[:20]}' "
            f"but found '{truncate_value(value=data['html'], max_length=20)}' "
            f"in upload response: {truncate_value(value=data, max_length=20)}"
        )
