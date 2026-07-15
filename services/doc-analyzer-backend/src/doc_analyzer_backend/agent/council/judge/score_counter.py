import logging

from src.doc_analyzer_backend.agent.models.council_assignments.judge_doc_data import JudgeDocData


logger = logging.getLogger(__name__)


async def count_scores(
    doc_judgement: JudgeDocData,
    doc_index: int | None = None,
) -> float | None:
    if doc_judgement.success_count > 0:
        average_answer_score = round(doc_judgement.answer_score / doc_judgement.success_count, 1)
        logger.info(
            f"Average score from {doc_judgement.success_count} judge agents: {average_answer_score}"
        )
        if doc_judgement.failed_count > 0:
            logger.info(
                f"Part of judges ({doc_judgement.failed_count}) failed to parse score from document {doc_index}"
            )
    else:
        average_answer_score = None
        logger.warning(
            f"All {doc_judgement.failed_count} judges failed to parse score for document {doc_index}"
        )
    return average_answer_score
