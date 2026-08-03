import allure
import pytest

from tests.assertions.http import assert_response_fail
from tests.consts.filelist import INVALID_FILELIST_PARAM_VALUE
from tests.factories.payloads.valid import make_filelist_params

FILES_LIST_PATH = "/files/list"


@allure.epic("Documents Analyzer AI Agent API")
@allure.feature(f"Получение списка файлов {FILES_LIST_PATH}")
class TestApiFilesListNegative:
    @allure.title(
        "Ошибка получения списка файлов при невалидном параметре {param_name}"
    )
    @allure.description(
        f"Запрос GET {FILES_LIST_PATH} возвращает 422 "
        "при передаче невалидного параметра."
    )
    @pytest.mark.parametrize(
        "param_name",
        [
            pytest.param("sort_by", id="invalid_sort_by"),
            pytest.param("sort_order", id="invalid_sort_order"),
            pytest.param("filter_ext", id="invalid_filter_ext"),
            pytest.param("page", id="invalid_page"),
            pytest.param("limit", id="invalid_limit"),
        ],
    )
    def test_get_files_list_invalid_param_fail(self, test_api_client, param_name):
        with allure.step(f"Выполнение запроса GET {FILES_LIST_PATH}"):
            params = make_filelist_params(**{param_name: INVALID_FILELIST_PARAM_VALUE})
            response = test_api_client.get(FILES_LIST_PATH, params=params)

        assert_response_fail(response=response, expected_status_code=422)

    @allure.title(
        'Ошибка получения списка файлов при невалидном значении параметра пагинации "page"'
    )
    @allure.description(
        f"Запрос GET {FILES_LIST_PATH} возвращает 422 "
        'при передаче невалидного значения пагинации "page".'
    )
    @pytest.mark.parametrize(
        "page",
        [
            pytest.param(0, id="invalid_page_0"),
            pytest.param(-1, id="invalid_page_-1"),
            pytest.param(-100, id="invalid_page_-100"),
        ],
    )
    def test_get_files_list_invalid_page_fail(self, test_api_client, page):
        with allure.step(f"Выполнение запроса GET {FILES_LIST_PATH}"):
            params = make_filelist_params(page=page)
            response = test_api_client.get(FILES_LIST_PATH, params=params)

        assert_response_fail(response=response, expected_status_code=422)

    @allure.title(
        'Ошибка получения списка файлов при невалидном значении пагинации "limit"'
    )
    @allure.description(
        f"Запрос GET {FILES_LIST_PATH} возвращает 422 "
        'при передаче невалидного значения пагинации "limit".'
    )
    @pytest.mark.parametrize(
        "limit",
        [
            pytest.param(0, id="invalid_limit_0"),
            pytest.param(-1, id="invalid_limit_-1"),
            pytest.param(-10, id="invalid_limit_-10"),
            pytest.param(101, id="invalid_border_limit_101"),
            pytest.param(200, id="invalid_limit_200"),
            pytest.param(1_000_000, id="invalid_limit_1_000_000"),
        ],
    )
    def test_get_files_list_invalid_limit_fail(self, test_api_client, limit):
        with allure.step(f"Выполнение запроса GET {FILES_LIST_PATH}"):
            params = make_filelist_params(limit=limit)
            response = test_api_client.get(FILES_LIST_PATH, params=params)

        assert_response_fail(response=response, expected_status_code=422)

    @allure.title("Ошибка получения списка файлов при указании файла вместо директории")
    @allure.description(
        f"Запрос GET {FILES_LIST_PATH} возвращает 400 "
        "при указании на файл вместо директории для чтения содержащегося внутри списка файлов."
    )
    def test_get_files_list_file_instead_of_dir_fail(
        self, test_api_client, mock_filelist_with_file_instead_of_dir_error
    ):
        with allure.step("Подготовка тестовых данных"):
            file_path = "file.txt"
            mock = mock_filelist_with_file_instead_of_dir_error(file_path)

        with allure.step(f"Выполнение запроса GET {FILES_LIST_PATH}"):
            response = test_api_client.get(FILES_LIST_PATH)

        assert_response_fail(
            response=response,
            expected_status_code=400,
            error_field_name="message",
            expected_error_message_part="Directory expected but file received",
        )

        with allure.step("Проверка, что агент не вызывался"):
            mock.list_files.assert_not_called()

    @allure.title(
        "Ошибка получения списка файлов, если при чтении содержимого директории выбросывается исключение"
    )
    @allure.description(
        f"Запрос GET {FILES_LIST_PATH} возвращает 500, "
        "если при чтении содержимого директории выбросывается исключение."
    )
    def test_get_files_list_exception_fail(
        self, test_api_client, mock_filelist_with_exception
    ):
        with allure.step("Подготовка тестовых данных"):
            error_message = "Unhandled exception"
            mock = mock_filelist_with_exception(error_message=error_message)

        with allure.step(f"Выполнение запроса GET {FILES_LIST_PATH}"):
            response = test_api_client.get(FILES_LIST_PATH)

        assert_response_fail(
            response=response,
            expected_status_code=500,
            error_field_name="message",
            expected_error_message_part=error_message,
        )

        with allure.step("Проверка, что агент не вызывался"):
            mock.list_files.assert_not_called()
