import logging

from agent_enums import Role

from src.doc_analyzer_backend.agent.agent import Agent
from src.doc_analyzer_backend.agent.council.corrector.corrector import correct_result
from src.doc_analyzer_backend.agent.models.consumption_data import ConsumptionData, create_consumption_data
from src.doc_analyzer_backend.agent.models.correction_data import CorrectionData
from src.doc_analyzer_backend.agent.runners.stage_runner import run_stage
from src.doc_analyzer_backend.api.models.analisys.answer_seq import AnswerSeq

logger = logging.getLogger(__name__)


async def run_corrector_stage(
    correctors: list[Agent],
    answer_seqs: list[AnswerSeq],
    role: Role,
    progress_callback=None,
) -> tuple[list[AnswerSeq], ConsumptionData]:
    logger.info(f"Council of {len(correctors)} CORRECTOR agents: correction is starting...")

    correctors_consumption_data = create_consumption_data()
    correction_data = CorrectionData(
        answer_seqs=answer_seqs,
        consumption_data=correctors_consumption_data,
    )
    empty_stage_consumption_data = create_consumption_data()

    correctors_result, _ = await run_stage(
        stage_name=f"Correctors ",
        stage_fn=lambda: correct_result(
            correctors=correctors,
            role=role,
            correction_data=correction_data,
            progress_callback=progress_callback,
        ),
        consumption_data=empty_stage_consumption_data,
    )
    logger.info(f"Council of {len(correctors)} CORRECTOR agents: correction is completed")

    return correctors_result.answer_seqs, correctors_consumption_data
