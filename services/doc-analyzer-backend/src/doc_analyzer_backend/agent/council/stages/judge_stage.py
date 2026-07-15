import logging

from agent_enums import Role

from src.doc_analyzer_backend.agent.agent import Agent
from src.doc_analyzer_backend.agent.council.judge.judge import judge_result
from src.doc_analyzer_backend.agent.models.tokens.consumption_data import ConsumptionData, create_consumption_data
from src.doc_analyzer_backend.agent.models.council_assignments.judgement_data import JudgementData
from src.doc_analyzer_backend.agent.runners.stage_runner import run_stage
from src.doc_analyzer_backend.api.models.analisys.answer_seq import AnswerSeq

logger = logging.getLogger(__name__)


async def run_judge_stage(
    judges: list[Agent],
    answer_seqs: list[AnswerSeq],
    role: Role,
    progress_callback=None,
) -> tuple[JudgementData, ConsumptionData]:
    logger.info(f"Council of {len(judges)} JUDGES agents: judgement is starting...")

    consumption_data = create_consumption_data()
    result = await run_stage(
        stage_name=f"{len(judges)} judges: judgement",
        stage_fn=lambda: judge_result(
            judges=judges,
            answer_seqs=answer_seqs,
            role=role,
            progress_callback=progress_callback,
        ),
        consumption_data=consumption_data,
    )
    logger.info(f"Council of {len(judges)} JUDGES agents: judgement is completed")

    return result
