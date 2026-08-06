import logging

from fastapi import APIRouter, Depends

from src.doc_analyzer_backend.api.config.backend_config import backend_config
from src.doc_analyzer_backend.api.dependencies.dependencies import get_user_session
from src.doc_analyzer_backend.api.models.config.config_response import ConfigResponse
from src.doc_analyzer_backend.api.models.status.health_check_response import (
    HealthCheckResponse,
)
from src.doc_analyzer_backend.api.models.status.status_response import (
    StatusResponse,
    ToolData,
    RAGData,
)
from src.doc_analyzer_backend.config.loader.settings import app_settings
from src.doc_analyzer_backend.session.data.user_session import UserSession

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def api_health_check():
    """Liveness probe: сервис поднят и отвечает"""
    try:
        model = app_settings().llm.model
        return HealthCheckResponse(status="OK", model=model)
    except Exception as e:
        logger.error(f"Healthcheck failed: {e}")
        return HealthCheckResponse(status="DEGRADED", model="unknown")


@router.get("/status", response_model=StatusResponse, response_model_exclude_none=True)
async def api_status():
    settings = app_settings()
    llm_config = settings.llm
    rag_config = settings.rag

    tools_data = [
        ToolData(
            name="read_document_file",
            description="Читает текстовый файл по указанному пути.",
        ),
        ToolData(
            name="read_web_page_from_url",
            description="Открывает веб-страницу по указанному URL и читает содержимое этой веб-страницы.",
        ),
    ]
    rag_data = (
        None
        if not rag_config.use_vector_db
        else RAGData(
            model=rag_config.embedding_model,
            top_k=rag_config.top_k,
            similarity_threshold=rag_config.similarity_threshold,
        )
    )
    return StatusResponse(
        model=llm_config.model,
        temperature=llm_config.temperature,
        tools=tools_data,
        use_rag=rag_config.use_vector_db,
        rag=rag_data,
    )


@router.get("/status/session", response_model=StatusResponse, response_model_exclude_none=True)
async def api_status_session(user: UserSession = Depends(get_user_session)):
    settings = app_settings()
    llm_config = settings.llm
    rag_config = settings.rag

    tools_data = []
    for tool in user.agent.tools:
        tools_data.append(
            ToolData(
                name=getattr(tool, "name", "unknown"),
                description=getattr(tool, "description", "unknown").split("\n")[0],
            )
        )
    rag_data = (
        None
        if not rag_config.use_vector_db
        else RAGData(
            model=rag_config.embedding_model,
            top_k=rag_config.top_k,
            similarity_threshold=rag_config.similarity_threshold,
        )
    )
    return StatusResponse(
        model=llm_config.model,
        temperature=llm_config.temperature,
        tools=tools_data,
        use_rag=rag_config.use_vector_db,
        rag=rag_data,
    )


@router.get("/config", response_model=ConfigResponse)
async def api_get_config():
    return backend_config
