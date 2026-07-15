import asyncio

from agent_enums import Role, Assignment

from src.doc_analyzer_backend.agent.agent import Agent
from src.doc_analyzer_backend.agent.models.analysis.agent_analysis_data import AgentAnalysisData
from src.doc_analyzer_backend.agent.runners.council_agent_runner import run_agent


async def run_judges_async(
    judges: list[Agent],
    last_answer: str,
    role: Role,
    progress_callback=None,
    doc_index: int | None = None,
) -> list[AgentAnalysisData]:
    return await asyncio.gather(
        *[
            run_agent(
                agent=judge,
                role=role,
                assignment=Assignment.JUDGE,
                resources=[last_answer],
                progress_callback=progress_callback,
                doc_index=doc_index,
            )
            for judge in judges
        ],
    )
