import os
from pathlib import Path
from typing import Any

from api.exceptions.exceptions import (
    AgentFileNotFoundError,
    AgentDirectoryInsteadOfFileError,
    AgentFileTooLargeForPreviewError,
    AgentUnsupportedFileExtensionError,
    AgentFilePreviewError,
)
from components.preview_reader.consts import CODE_LANGS, IMAGE_MIMES
from components.preview_reader.preview_parsers import (
    parse_text,
    parse_markup,
    parse_data,
    parse_csv,
    parse_code,
    parse_docx,
    parse_xlsx,
    parse_pptx,
    parse_pdf,
    parse_image,
)


def file_preview(file_path: str, max_size: int) -> dict[str, Any]:
    """
    Читает файл любого поддерживаемого формата и возвращает структуру,
    оптимизированную для отрисовки в React.
    """
    if not os.path.exists(file_path):
        raise AgentFileNotFoundError(file_path)

    if os.path.isdir(file_path):
        raise AgentDirectoryInsteadOfFileError(file_path)

    file_size = os.path.getsize(file_path)
    if file_size > max_size:
        raise AgentFileTooLargeForPreviewError(file_path, file_size)

    path = Path(file_path).resolve()
    ext = path.suffix.lower()

    handlers = {
        ".txt": parse_text,
        ".md": parse_text,
        ".html": parse_markup,
        ".xml": parse_markup,
        ".json": parse_data,
        ".yaml": parse_data,
        ".yml": parse_data,
        ".csv": parse_csv,
        ".bash": parse_code,
        ".zsh": parse_code,
        ".sh": parse_code,
        ".docx": parse_docx,
        ".xlsx": parse_xlsx,
        ".pptx": parse_pptx,
        ".pdf": parse_pdf,
    }

    handler = handlers.get(ext) or (
        parse_code if ext in CODE_LANGS else parse_image if ext in IMAGE_MIMES else None
    )
    if not handler:
        raise AgentUnsupportedFileExtensionError(file_path)

    try:
        blocks, metadata = handler(path)
        return {
            "status": "success",
            "filename": path.name,
            "format": ext,
            "metadata": metadata,
            "blocks": blocks,
        }
    except Exception:
        raise AgentFilePreviewError(file_path)
