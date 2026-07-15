import asyncio
import logging

from agent_enums import Assignment, Role

from src.doc_analyzer_backend.agent.agent import Agent
from src.doc_analyzer_backend.agent.models.analysis.agent_analysis_data import AgentAnalysisData
from src.doc_analyzer_backend.agent.models.tokens.consumption_data import ConsumptionData, create_consumption_data
from src.doc_analyzer_backend.agent.runners.council_agent_runner import run_agent
from src.doc_analyzer_backend.api.models.analisys.answer_seq import AnswerSeq

logger = logging.getLogger(__name__)


async def run_exec_stage(
    agents: list[Agent],
    resources: list[str],
    role: Role,
    progress_callback=None,
) -> tuple[list[AnswerSeq], ConsumptionData]:
    logger.info(f"Council of {len(agents)} EXEC agents: doc analysis is starting...")
    results = await _run_exec_agents(
        agents=agents,
        resources=resources,
        role=role,
        progress_callback=progress_callback,
    )
    stage_result = await _process_exec_results(results=results)
    logger.info(f"Council of {len(agents)} EXEC agents: doc analysis is completed")
    return stage_result


async def _run_exec_agents(
    agents: list[Agent],
    role: Role,
    resources: list[str],
    progress_callback=None,
) -> list[AgentAnalysisData]:
    results = list(
        await asyncio.gather(
            *[
                run_agent(
                    agent=agent,
                    role=role,
                    assignment=Assignment.EXEC,
                    resources=resources,
                    progress_callback=progress_callback,
                )
                for agent in agents
            ],
        )
    )
    return results


async def _process_exec_results(
    results: list[AgentAnalysisData],
) -> tuple[list[AnswerSeq], ConsumptionData]:
    answer_seqs = []
    consumption_data = create_consumption_data()

    for r in results:
        answer_seqs.append(AnswerSeq(answers=[r.answer_item]))
        consumption_data.update_by_data(r.consumption_data)

    logger.info(f"Exec token usage: {consumption_data.token_usage}")
    logger.info(f"Exec cost: {consumption_data.cost}")
    return answer_seqs, consumption_data
