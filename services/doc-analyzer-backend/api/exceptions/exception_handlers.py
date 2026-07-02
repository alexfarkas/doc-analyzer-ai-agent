import logging

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from api.api import app
from api.exceptions.exceptions import (
    AgentFileNotFoundError,
    AgentDirectoryInsteadOfFileError,
    AgentFileInsteadOfDirectoryError,
    AgentFileTooLargeForPreviewError,
    AgentUnsupportedFileExtensionError,
    AgentFilePreviewError,
    AgentsListIsEmptyError,
)

logger = logging.getLogger(__name__)


@app.exception_handler(AgentFileNotFoundError)
async def agent_file_not_found_exception_handler(
    request: Request, exc: AgentFileNotFoundError
):
    return JSONResponse(status_code=404, content={"message": exc.message})


@app.exception_handler(AgentDirectoryInsteadOfFileError)
async def agent_directory_instead_of_file_exception_handler(
    request: Request, exc: AgentDirectoryInsteadOfFileError
):
    return JSONResponse(status_code=400, content={"message": exc.message})


@app.exception_handler(AgentFileInsteadOfDirectoryError)
async def agent_file_instead_of_directory_exception_handler(
    request: Request, exc: AgentFileInsteadOfDirectoryError
):
    return JSONResponse(status_code=400, content={"message": exc.message})


@app.exception_handler(AgentsListIsEmptyError)
async def agents_list_is_empty_exception_handler(
    request: Request, exc: AgentsListIsEmptyError
):
    return JSONResponse(status_code=422, content={"message": exc.message})


@app.exception_handler(AgentFileTooLargeForPreviewError)
async def agent_file_too_large_for_preview_exception_handler(
    request: Request, exc: AgentFileTooLargeForPreviewError
):
    return JSONResponse(status_code=413, content={"message": exc.message})


@app.exception_handler(AgentUnsupportedFileExtensionError)
async def agent_unsupported_file_extension_exception_handler(
    request: Request, exc: AgentUnsupportedFileExtensionError
):
    return JSONResponse(status_code=400, content={"message": exc.message})


@app.exception_handler(AgentFilePreviewError)
async def agent_file_preview_exception_handler(
    request: Request, exc: AgentFilePreviewError
):
    return JSONResponse(status_code=500, content={"message": exc.message})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc

    logger.error(f"Unhandled exception on request {request.url}: {exc}", exc_info=True)

    return JSONResponse(status_code=500, content={"message": "Unhandled exception"})
