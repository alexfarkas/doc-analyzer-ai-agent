import logging
from typing import Literal

from fastapi import UploadFile, File, Query, APIRouter

from src.doc_analyzer_backend.api.models.files.files_list_response import (
    FilesListResponse,
    FilesPaginationResponse,
)
from src.doc_analyzer_backend.api.models.files.files_preview_response import (
    FilesPreviewResponse,
)
from src.doc_analyzer_backend.api.models.upload.upload_file_response import (
    UploadFileResponse,
)
from src.doc_analyzer_backend.api.models.upload.upload_from_url_request import (
    UploadFromUrlRequest,
)
from src.doc_analyzer_backend.api.models.upload.upload_from_url_response import (
    UploadFromUrlResponse,
)
from src.doc_analyzer_backend.components.file_manager.file_manager import list_files
from src.doc_analyzer_backend.components.preview_reader.preview_reader import (
    file_preview,
)
from src.doc_analyzer_backend.components.uploader.file_uploader import upload_file
from src.doc_analyzer_backend.components.uploader.web_content_uploader import (
    upload_content_from_url,
)
from src.doc_analyzer_backend.config.app_config import app_config

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload/file", response_model=UploadFileResponse)
async def api_upload_file(file: UploadFile = File(...)):
    result = await upload_file(file)
    return UploadFileResponse(
        file_path=result["file_path"], filename=result["filename"]
    )


@router.post("/upload/from-url", response_model=UploadFromUrlResponse)
async def api_upload_from_url(request: UploadFromUrlRequest):
    text = upload_content_from_url(request.url)
    return UploadFromUrlResponse(url=request.url, html=text)


@router.get("/files/preview", response_model=FilesPreviewResponse)
async def api_files_preview(
    file_path: str = Query(..., description="File path"),
    max_size: int = Query(
        app_config.max_file_preview_size, description="Max file size"
    ),
):
    result = file_preview(file_path, max_size)
    return FilesPreviewResponse(
        status=result["status"],
        filename=result["filename"],
        format=result["format"],
        metadata=result["metadata"],
        blocks=result["blocks"],
    )


@router.get("/files/list", response_model=FilesListResponse)
async def api_files_list(
    sort_by: Literal["name", "ext", "size", "created_at"] = Query(
        "name", description="Sort files"
    ),
    sort_order: Literal["asc", "desc"] = Query("asc", description="Sort order"),
    filter_ext: str | None = Query(None, description="Filter files by extension"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Files on page"),
):
    docs_dir = app_config.docs_dir

    result = list_files(docs_dir, sort_by, sort_order, filter_ext, page, limit)
    pagination = result["pagination"]

    return FilesListResponse(
        files=result["paginated_files"],
        pagination=FilesPaginationResponse(
            current_page=pagination["current_page"],
            total_pages=pagination["total_pages"],
            files_on_page=pagination["files_on_page"],
            total_files=pagination["total_files"],
        ),
    )
