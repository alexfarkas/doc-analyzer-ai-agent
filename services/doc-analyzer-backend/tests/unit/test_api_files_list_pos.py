import allure
import pytest

from tests.assertions.filelist import (
    assert_filelist_response_body,
    assert_filelist_agent_call,
    assert_filelist_agent_call_all_params,
    assert_file_data,
)
from tests.assertions.http import assert_response_success
from tests.consts.filelist import (
    EXPECTED_FILELIST_SORT_FIELDS,
    EXPECTED_FILELIST_SORT_ORDERS,
    EXPECTED_FILELIST_FILTER_EXTENSIONS,
    MAX_FILELIST_LIMIT,
)
from tests.factories.mocks import (
    make_filelist_result,
    make_file_items,
    make_empty_filelist_result,
)
from tests.factories.payloads.valid import (
    make_filelist_params,
    make_filelist_all_params,
    make_file_data,
)

FILES_LIST_PATH = "/files/list"


@allure.epic("Documents Analyzer AI Agent API")
@allure.feature(f"Получение списка файлов {FILES_LIST_PATH}")
class TestApiFilesListPositive:
    @allure.title("Получение списков с разным количеством файлов")
    @allure.description(
        f"Запрос GET {FILES_LIST_PATH} возвращает 200 OK и список в теле ответа "
        "для разного количества файлов."
    )
    @pytest.mark.parametrize(
        "files_count",
        [
            pytest.param(1, id="single_file_in_list"),
            pytest.param(5, id="5_files_in_list"),
            pytest.param(100, id="100_files_in_list"),
        ],
    )
    def test_get_files_list_success(self, test_api_client, mock_filelist, files_count):
        with allure.step("Подготовка тестовых данных"):
            files_list = make_filelist_result(files=make_file_items(count=files_count))
            mock_filelist(files_list)

        with allure.step(f"Выполнение запроса GET {FILES_LIST_PATH}"):
            response = test_api_client.get(FILES_LIST_PATH)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_filelist_response_body(
            data=data, expected_data=files_list, files_count=files_count
        )

    @allure.title("Получение списка файлов с сортировкой по {sort_by}")
    @allure.description(
        f"Запрос GET {FILES_LIST_PATH} возвращает 200 OK и список в теле ответа "
        "с сортировкой по заданным параметрам."
    )
    @pytest.mark.parametrize(
        "sort_by",
        [
            pytest.param(sort_by, id=sort_by)
            for sort_by in EXPECTED_FILELIST_SORT_FIELDS
        ],
    )
    def test_get_files_list_sort_by_success(
        self, test_api_client, mock_filelist, sort_by
    ):
        with allure.step("Подготовка тестовых данных"):
            params = make_filelist_params(sort_by=sort_by)

            files_list = make_filelist_result()
            mock = mock_filelist(files_list)

        with allure.step(f"Выполнение запроса GET {FILES_LIST_PATH}"):
            response = test_api_client.get(FILES_LIST_PATH, params=params)

        assert_response_success(response=response, expected_status_code=200)

        assert_filelist_agent_call(mock=mock, param="sort_by", expected_value=sort_by)

    @allure.title("Получение списка файлов с заданным порядком сортировки {sort_order}")
    @allure.description(
        f"Запрос GET {FILES_LIST_PATH} возвращает 200 OK и список в теле ответа "
        "с заданным порядком сортировки."
    )
    @pytest.mark.parametrize(
        "sort_order",
        [
            pytest.param(sort_order, id=sort_order)
            for sort_order in EXPECTED_FILELIST_SORT_ORDERS
        ],
    )
    def test_get_files_list_sort_order_success(
        self, test_api_client, mock_filelist, sort_order
    ):
        with allure.step("Подготовка тестовых данных"):
            params = make_filelist_params(sort_order=sort_order)

            files_list = make_filelist_result()
            mock = mock_filelist(files_list)

        with allure.step(f"Выполнение запроса GET {FILES_LIST_PATH}"):
            response = test_api_client.get(FILES_LIST_PATH, params=params)

        assert_response_success(response=response, expected_status_code=200)

        assert_filelist_agent_call(
            mock=mock, param="sort_order", expected_value=sort_order
        )

    @allure.title("Получение списка файлов с фильтрацией по расширению")
    @allure.description(
        f"Запрос GET {FILES_LIST_PATH} возвращает 200 OK и список в теле ответа "
        "с фильтрацией по расширению."
    )
    @pytest.mark.parametrize(
        "filter_ext",
        [pytest.param(ext, id=ext) for ext in EXPECTED_FILELIST_FILTER_EXTENSIONS],
    )
    def test_get_files_list_filter_ext_success(
        self, test_api_client, mock_filelist, filter_ext
    ):
        with allure.step("Подготовка тестовых данных"):
            params = make_filelist_params(filter_ext=filter_ext)

            files_list = make_filelist_result()
            mock = mock_filelist(files_list)

        with allure.step(f"Выполнение запроса GET {FILES_LIST_PATH}"):
            response = test_api_client.get(FILES_LIST_PATH, params=params)

        assert_response_success(response=response, expected_status_code=200)

        assert_filelist_agent_call(
            mock=mock, param="filter_ext", expected_value=filter_ext
        )

    @allure.title("Получение списка файлов с пагинацией")
    @allure.description(
        f"Запрос GET {FILES_LIST_PATH} возвращает 200 OK и список с пагинацией в теле ответа."
    )
    @pytest.mark.parametrize(
        "page, limit",
        [
            pytest.param(1, 10, id="pagination_page_1_limit_10"),
            pytest.param(1, 50, id="pagination_page_1_limit_50"),
            pytest.param(2, 10, id="pagination_page_2_limit_10"),
            pytest.param(3, 40, id="pagination_page_3_limit_30"),
        ],
    )
    def test_get_files_list_pagination_success(
        self, test_api_client, mock_filelist, page, limit
    ):
        with allure.step("Подготовка тестовых данных"):
            params = make_filelist_params(page=page, limit=limit)
            files_list = make_filelist_result(current_page=page)
            mock = mock_filelist(files_list)

        with allure.step(f"Выполнение запроса GET {FILES_LIST_PATH}"):
            response = test_api_client.get(FILES_LIST_PATH, params=params)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_filelist_response_body(data=data, expected_data=files_list)

        assert_filelist_agent_call(mock=mock, param="page", expected_value=page)
        assert_filelist_agent_call(mock=mock, param="limit", expected_value=limit)

    @allure.title('Получение списка файлов с максимальным значением параметра "limit"')
    @allure.description(
        f"Запрос GET {FILES_LIST_PATH} возвращает 200 OK и список с пагинацией в теле ответа "
        'с максимальным значением параметра "limit": максимального количества имен файлов '
        "на одной странице пагинации."
    )
    def test_get_files_list_max_limit_success(self, test_api_client, mock_filelist):
        with allure.step("Подготовка тестовых данных"):
            params = make_filelist_params(limit=MAX_FILELIST_LIMIT)
            files_list = make_filelist_result(files_on_page=MAX_FILELIST_LIMIT)
            mock = mock_filelist(files_list)

        with allure.step(f"Выполнение запроса GET {FILES_LIST_PATH}"):
            response = test_api_client.get(FILES_LIST_PATH, params=params)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_filelist_response_body(data=data, expected_data=files_list)
        assert_filelist_agent_call(
            mock=mock, param="limit", expected_value=MAX_FILELIST_LIMIT
        )

    @allure.title("Получение пустого списка файлов для пустой директории")
    @allure.description(
        f"Запрос GET {FILES_LIST_PATH} возвращает 200 OK и пустой список в теле ответа "
        "для пустой директории."
    )
    def test_get_files_list_empty_dir_success(self, test_api_client, mock_filelist):
        with allure.step("Подготовка тестовых данных"):
            files_list = make_empty_filelist_result()
            mock_filelist(files_list)

        with allure.step(f"Выполнение запроса GET {FILES_LIST_PATH}"):
            response = test_api_client.get(FILES_LIST_PATH)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_filelist_response_body(data=data, expected_data=files_list)

    @allure.title("Получение списка файлов с комбинацией параметров")
    @allure.description(
        "Запрос GET /files/list возвращает 200 OK и список в теле ответа "
        "с комбинацией параметров."
    )
    def test_get_files_list_params_combination_success(
        self, test_api_client, mock_filelist
    ):
        with allure.step("Подготовка тестовых данных"):
            params = make_filelist_all_params()

            files_list = make_filelist_result()
            mock = mock_filelist(files_list)

        with allure.step(f"Выполнение запроса GET {FILES_LIST_PATH}"):
            response = test_api_client.get(FILES_LIST_PATH, params=params)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_filelist_response_body(data=data, expected_data=files_list)
        assert_filelist_agent_call_all_params(mock=mock, expected_values=params)

    @allure.title("Корректная структура данных о файле в списке")
    @allure.description(
        f"Запрос GET {FILES_LIST_PATH} возвращает 200 OK и список в теле ответа "
        "с корректной структурой данных у файлов."
    )
    def test_get_files_list_valid_file_data_structure_success(
        self, test_api_client, mock_filelist
    ):
        with allure.step("Подготовка тестовых данных"):
            file_data = make_file_data()
            files_list = make_filelist_result(files=file_data)
            mock_filelist(files_list)

        with allure.step(f"Выполнение запроса GET {FILES_LIST_PATH}"):
            response = test_api_client.get(FILES_LIST_PATH)

        data = assert_response_success(response=response, expected_status_code=200)

        assert_file_data(data=data, expected_data=file_data)
