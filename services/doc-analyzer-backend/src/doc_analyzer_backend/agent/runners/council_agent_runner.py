import logging

from agent_enums import Role, Assignment

from src.doc_analyzer_backend.agent.agent import Agent
from src.doc_analyzer_backend.agent.messages_data.progress_data import (
    start_event,
    stop_event,
)
from src.doc_analyzer_backend.agent.models.analysis.agent_analysis_data import (
    AgentAnalysisData,
)

logger = logging.getLogger(__name__)


async def run_agent(
    agent: Agent,
    role: Role,
    assignment: Assignment,
    resources: list[str],
    progress_callback=None,
    doc_index: int | None = None,
) -> AgentAnalysisData:
    if progress_callback:
        await progress_callback(start_event(agent.agent_id, assignment))

    doc_logging = f" of document {doc_index}" if doc_index else ""

    logger.info(
        f"Agent {agent.agent_id} ({assignment.value}): processing{doc_logging} is starting..."
    )
    try:
        return await agent.analyze_doc(
            resources=resources,
            role=role,
            assignment=assignment,
        )
    finally:
        logger.info(
            f"Agent {agent.agent_id} ({assignment.value}): processing{doc_logging} is completed"
        )
        if progress_callback:
            await progress_callback(stop_event(agent.agent_id, assignment))
