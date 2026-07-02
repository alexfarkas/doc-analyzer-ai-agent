from pydantic import BaseModel


class FilesListResponse(BaseModel):
    files: list[FileDataResponse]
    pagination: FilesPaginationResponse


class FileDataResponse(BaseModel):
    name: str
    extension: str
    size: int
    created_at: str


class FilesPaginationResponse(BaseModel):
    current_page: int
    total_pages: int
    files_on_page: int
    total_files: int
