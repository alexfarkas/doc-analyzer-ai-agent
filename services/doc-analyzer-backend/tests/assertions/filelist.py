from unittest.mock import Mock

import allure


def assert_filelist_response_body(
    data: dict, expected_data: dict, files_count: int | None = None
):
    with allure.step("Проверка тела ответа списка файлов"):
        for field in ["files", "pagination"]:
            assert field in data, f"No '{field}' field in files list response: {data}"

        if files_count:
            assert len(data["files"]) == files_count

        pagination = data["pagination"]
        expected_pagination = expected_data["pagination"]
        for field in ["current_page", "total_pages", "files_on_page", "total_files"]:
            assert pagination[field] == expected_pagination[field], (
                f"Expected {field} '{expected_pagination[field]}' "
                f"but found '{pagination[field]}' in files list pagination response: {pagination}"
            )


def assert_filelist_agent_call_all_params(mock: Mock, expected_values: dict):
    for param in ["sort_by", "sort_order", "filter_ext", "page", "limit"]:
        assert_filelist_agent_call(
            mock=mock, param=param, expected_value=expected_values[param]
        )


def assert_filelist_agent_call(mock: Mock, param: str, expected_value: str | int):
    with allure.step("Проверка вызова агента"):
        mock.assert_called_once()
        call_args = mock.call_args

        match param:
            case "sort_by":
                index = 1
            case "sort_order":
                index = 2
            case "filter_ext":
                index = 3
            case "page":
                index = 4
            case "limit":
                index = 5

        assert call_args[0][index] == expected_value

def assert_file_data(data: dict, expected_data: list[dict], file_index: int = 0):
    with allure.step("Проверка структуры данных файла в ответе списка файлов"):
        assert len(data["files"]) > 0

        file = data["files"][file_index]
        expected_file = expected_data[file_index]

        for field in ["name", "extension", "size", "created_at"]:
            assert file[field] == expected_file[field], (
                f"Expected {field} '{expected_file[field]}' "
                f"but found '{file[field]}' in file data response: {file}"
            )
