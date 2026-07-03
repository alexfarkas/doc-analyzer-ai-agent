import asyncio
import logging
import re

from agent_enums import Role, Assignment

from agent.agent import Agent
from llm.token_usage import create_token_usage

logger = logging.getLogger(__name__)


async def judge_result(
    judges: list[Agent],
    answers: list[str],
    role: Role,
    progress_callback=None,
) -> dict:
    judgements = []
    scores = []
    judges_token_usage = create_token_usage()
    judges_elapsed = 0

    async def run_judge(judge: Agent, answer: str) -> dict:
        if progress_callback:
            await progress_callback(
                "agent_start",
                {
                    "agentId": judge.agent_id,
                    "agentType": "judge",
                },
            )
        logger.info(
            f"Agent {judge.agent_id} (judge): judgement for document {answer_index} is starting..."
        )
        try:
            return await judge.analyze_doc(
                resources=[answer], role=role, assignment=Assignment.JUDGE
            )
        finally:
            logger.info(
                f"Agent {judge.agent_id} (judge): judgement for document {answer_index} is completed"
            )
            if progress_callback:
                await progress_callback(
                    "agent_end",
                    {
                        "agentId": judge.agent_id,
                        "agentType": "judge",
                    },
                )

    for answer_index, answer in enumerate(answers, start=1):
        answer_score = 0
        failed_scores = 0
        logger.info(f"Judgment for document {answer_index} is starting...")

        results = await asyncio.gather(
            *[run_judge(judge, answer) for judge in judges],
        )

        answer_judgements = [r["answer"] for r in results]

        for result in results:
            parsed_score = re.search(
                r"(?i)Оценка\s*:?\s*[\[\(]?\s*(\d+)\s*[\]\)]?", result["answer"]
            )

            if not parsed_score:
                scores.append(None)
                failed_scores += 1
                logger.error(
                    f"Error parsing score from judge agent answer {result["answer"][:15]}"
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

            judges_token_usage.add_usage(result["token_usage"])
            judges_elapsed += result["elapsed"]

        logger.info(f"Judgment for document {answer_index} is completed")

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
