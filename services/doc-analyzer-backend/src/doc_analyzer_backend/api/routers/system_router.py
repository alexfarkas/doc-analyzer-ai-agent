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
from src.doc_analyzer_backend.config.llm_config import llm_config
from src.doc_analyzer_backend.config.rag_config import rag_config
from src.doc_analyzer_backend.session.data.user_session import UserSession

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def api_health_check(user: UserSession = Depends(get_user_session)):
    """Проверка готовности сервиса"""
    status = "OK" if user.agent is not None else "Agent is not initialized"
    return HealthCheckResponse(status=status, model=llm_config.model)


@router.get("/status", response_model=StatusResponse, response_model_exclude_none=True)
async def api_status(user: UserSession = Depends(get_user_session)):
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
async def api_get_config(user: UserSession = Depends(get_user_session)):
    return backend_config
