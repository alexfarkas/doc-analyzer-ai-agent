from typing import Any

from pydantic import BaseModel


class FilesPreviewResponse(BaseModel):
    status: str
    filename: str
    format: str
    metadata: Any
    blocks: Any
