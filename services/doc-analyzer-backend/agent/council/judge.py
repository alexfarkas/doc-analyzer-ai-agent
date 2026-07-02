import logging
import re

from agent_enums import Role, Assignment

from agent.agent import Agent
from llm.token_usage import create_token_usage

logger = logging.getLogger(__name__)


async def judge_result(judges: list[Agent], answers: list[str], role: Role) -> dict:
    judgements = []
    scores = []
    judges_token_usage = create_token_usage()
    judges_elapsed = 0

    for answer_index, answer in enumerate(answers, start=1):
        answer_judgements = []
        answer_score = 0
        failed_scores = 0
        logger.info(f"Judgment for document {answer_index} is starting...")

        for index, judge in enumerate(judges, start=1):
            logger.info(
                f"Judge {index}: judgement for document {answer_index} is starting..."
            )
            result = await judge.analyze_doc(
                resources=[answer], role=role, assignment=Assignment.JUDGE
            )
            logger.info(
                f"Judge {index}: judgement for document {answer_index} is completed"
            )

            answer_judgement = result["answer"]
            answer_judgements.append(answer_judgement)

            parsed_score = re.search(
                r"(?i)Оценка\s*:?\s*[\[\(]?\s*(\d+)\s*[\]\)]?", answer_judgement
            )

            if not parsed_score:
                scores.append(None)
                failed_scores += 1
                logger.error(
                    f"Error parsing score from judge agent answer {answer_judgement[:15]}"
                )
            else:
                score = parsed_score.group(1)
                try:
                    answer_score += int(score)
                    logger.info(f"Judge agent score: {score}")
                except ValueError:
                    scores.append(None)
                    failed_scores += 1
                    logger.error(
                        f"Error receiving score from judge agent answer: {score}"
                    )

            token_usage = result["token_usage"]
            elapsed = result["elapsed"]

            judges_token_usage.add_usage(token_usage)
            judges_elapsed += elapsed

        logger.info(f"Judgment for document {answer_index + 1} is completed")

        judgements_summary = "\n\n".join(
            f"Судья {i + 1}:\n\n{j}" for i, j in enumerate(answer_judgements)
        )
        judgements.append(judgements_summary)

        average_answer_score = int(round(answer_score / (len(judges) - failed_scores)))
        logger.info(
            f"Average score from {len(judges)} judge agents: {average_answer_score}"
        )
        scores.append(average_answer_score)

    return {
        "judgements": judgements,
        "scores": scores,
        "judges_token_usage": judges_token_usage,
        "judges_elapsed": judges_elapsed,
    }
