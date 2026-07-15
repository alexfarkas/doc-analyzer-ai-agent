import logging
import re

from src.doc_analyzer_backend.agent.models.analysis.agent_analysis_data import (
    AgentAnalysisData,
)
from src.doc_analyzer_backend.agent.models.tokens.consumption_data import (
    create_consumption_data,
)
from src.doc_analyzer_backend.agent.models.council_assignments.judge_doc_data import (
    JudgeDocData,
)

logger = logging.getLogger(__name__)


SCORE_PATTERN = r"(?i)Оценка\s*:?\s*[\[\(]?\s*(\d+)\s*[\]\)]?"


async def judge_document(
    results: list[AgentAnalysisData],
) -> JudgeDocData:
    answer_judgements = []
    answer_score = 0
    success_count = len(results)
    failed_count = 0

    consumption_data = create_consumption_data()

    for result in results:
        answer = result.answer_item.answer

        answer_judgements.append(answer)

        score, failed_count = _parse_score(answer)
        answer_score += score
        failed_count += failed_count
        success_count -= failed_count

        consumption_data.update_by_data(result.consumption_data)

    return JudgeDocData(
        answer_judgements=answer_judgements,
        answer_score=answer_score,
        success_count=success_count,
        failed_count=failed_count,
        consumption_data=consumption_data,
    )


def _parse_score(answer: str) -> tuple[float, int]:
    parsed_score = re.search(SCORE_PATTERN, answer)

    if not parsed_score:
        logger.error(f"Error parsing score from judge agent answer {answer[:15]}")
        return 0, 1
    else:
        score = parsed_score.group(1)
        try:
            logger.info(f"Judge agent score: {score}")
            return int(score), 0
        except ValueError:
            logger.error(f"Error receiving score from judge agent answer: {score}")
            return 0, 1
