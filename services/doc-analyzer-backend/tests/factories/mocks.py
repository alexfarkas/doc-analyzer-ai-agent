from types import SimpleNamespace

from tests.consts.filelist import (
    DEFAULT_FILELIST_FILE_BASE_NAME,
    DEFAULT_FILELIST_FILE_EXT,
    DEFAULT_FILELIST_FILE_SIZE,
    DEFAULT_PAGINATION_CURRENT_PAGE,
    DEFAULT_PAGINATION_TOTAL_PAGES,
    DEFAULT_PAGINATION_FILES_ON_PAGE,
)


def make_tool_mock(name: str, description: str) -> SimpleNamespace:
    """
    LLM tool mock

    Args:
        name: tool name
        description: tool description

    Returns:
        Tool mock
    """
    return SimpleNamespace(name=name, description=description)


def make_upload_result_mock(
    file_path: str,
    filename: str,
) -> dict:
    """
    Upload file mock result

    Args:
        file_path: path to directory
        filename: file name

    Returns:
        Upload file mock data
    """
    return {"file_path": file_path, "filename": filename}


def make_empty_filelist_result() -> dict:
    return make_filelist_result(
        files=[],
        current_page=0,
        total_pages=0,
        files_on_page=0,
        total_files=0,
    )


def make_filelist_result(
    files: list | None = None,
    current_page: int = DEFAULT_PAGINATION_CURRENT_PAGE,
    total_pages: int = DEFAULT_PAGINATION_TOTAL_PAGES,
    files_on_page: int = DEFAULT_PAGINATION_FILES_ON_PAGE,
    total_files: int | None = None,
) -> dict:
    if files is None:
        files = make_file_items(count=files_on_page)
    if total_files is None:
        total_files = len(files)
    return {
        "paginated_files": files,
        "pagination": {
            "current_page": current_page,
            "total_pages": total_pages,
            "files_on_page": files_on_page,
            "total_files": total_files,
        },
    }


def make_file_items(count: int = 5):
    return [
        {
            "name": f"{DEFAULT_FILELIST_FILE_BASE_NAME}_{i}.{DEFAULT_FILELIST_FILE_EXT}",
            "extension": DEFAULT_FILELIST_FILE_EXT,
            "size": DEFAULT_FILELIST_FILE_SIZE,
            "created_at": f"2000-01-{i + 1:02d}T12:00:00",
        }
        for i in range(count)
    ]
