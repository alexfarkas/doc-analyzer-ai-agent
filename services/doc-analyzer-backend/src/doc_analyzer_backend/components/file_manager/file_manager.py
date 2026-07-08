from datetime import datetime
from pathlib import Path

from src.doc_analyzer_backend.api.exceptions.exceptions import AgentFileInsteadOfDirectoryError
from src.doc_analyzer_backend.config.app_config import app_config


def list_files(
    docs_dir: str,
    sort_by: str,
    sort_order: str,
    filter_ext: str | None,
    page: int,
    limit: int,
):
    files_path = Path(app_config.docs_dir).resolve()

    if not files_path.is_dir():
        raise AgentFileInsteadOfDirectoryError(docs_dir)

    if not files_path.exists():
        return {
            "paginated_files": [],
            "pagination": {
                "current_page": 0,
                "total_pages": 0,
                "files_on_page": 0,
                "total_files": 0,
            },
        }

    files = []
    for file in files_path.iterdir():
        if file.is_file() and not file.name.startswith("."):
            stat = file.stat()
            try:
                ts = stat.st_birthtime
            except AttributeError:
                ts = stat.st_ctime

            files.append(
                {
                    "name": file.name,
                    "extension": file.suffix.lower().replace(".", ""),
                    "size": file.stat().st_size,
                    "created_at": datetime.fromtimestamp(ts).isoformat(),
                }
            )

    if filter_ext is not None:
        files = [f for f in files if f.extension.lower() == filter_ext.lower()]

    sort_params = {
        "name": "name",
        "ext": "extension",
        "size": "size",
        "created_at": "created_at",
    }
    default_sort_priority = ["name", "ext", "size", "created_at"]

    def get_multi_sort_key(f):
        sort_priority = [sort_by] + [
            item for item in default_sort_priority if item != sort_by
        ]
        return tuple(f[sort_params[field]] for field in sort_priority)

    files.sort(key=get_multi_sort_key, reverse=(sort_order == "desc"))

    total_files = len(files)
    start = (page - 1) * limit
    end = start + limit
    paginated_files = files[start:end]
    total_pages = max(1, (total_files + limit - 1) // limit) if total_files > 0 else 0

    return {
        "paginated_files": paginated_files,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "files_on_page": limit,
            "total_files": total_files,
        },
    }
