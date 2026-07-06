import asyncio
import logging
import re

from agent_enums import Role, Assignment

from agent.agent import Agent
from agent.models.agent_analysis_data import AgentAnalysisData
from agent.models.judgement_data import JudgementData
from api.models.analisys.answer_seq import AnswerSeq
from llm.tokens.token_usage import create_token_usage

logger = logging.getLogger(__name__)


async def judge_result(
    judges: list[Agent],
    answer_seqs: list[AnswerSeq],
    role: Role,
    progress_callback=None,
) -> JudgementData:
    judgements = []
    scores = []
    judges_token_usage = create_token_usage()
    judges_elapsed = 0

    async def run_judge(judge: Agent, answer: str, seq_index: int) -> AgentAnalysisData:
        if progress_callback:
            await progress_callback(
                "agent_start",
                {
                    "agentId": judge.agent_id,
                    "agentType": "judge",
                },
            )
        logger.info(
            f"Agent {judge.agent_id} (judge): judgement for document {seq_index} is starting..."
        )
        try:
            return await judge.analyze_doc(
                resources=[answer], role=role, assignment=Assignment.JUDGE
            )
        finally:
            logger.info(
                f"Agent {judge.agent_id} (judge): judgement for document {seq_index} is completed"
            )
            if progress_callback:
                await progress_callback(
                    "agent_end",
                    {
                        "agentId": judge.agent_id,
                        "agentType": "judge",
                    },
                )

    for seq_index, seq in enumerate(answer_seqs, start=1):
        answer_score = 0
        failed_scores = 0
        logger.info(f"Judgment for document {seq_index} is starting...")

        last_answer = seq.answers[-1].answer
        results = await asyncio.gather(
            *[run_judge(judge, last_answer, seq_index) for judge in judges],
        )

        answer_judgements = [r.answer_item.answer for r in results]

        for result in results:
            answer = result.answer_item.answer
            parsed_score = re.search(
                r"(?i)Оценка\s*:?\s*[\[\(]?\s*(\d+)\s*[\]\)]?", answer
            )

            if not parsed_score:
                scores.append(None)
                failed_scores += 1
                logger.error(
                    f"Error parsing score from judge agent answer {answer[:15]}"
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

            judges_token_usage.add_usage(result.token_usage)
            judges_elapsed += result.elapsed

        logger.info(f"Judgment for document {seq_index} is completed")

        judgements_summary = "\n\n".join(
            f"Судья {i + 1}:\n\n{j}" for i, j in enumerate(answer_judgements)
        )
        judgements.append(judgements_summary)

        successful_scores = len(judges) - failed_scores
        if successful_scores > 0:
            average_answer_score = round(answer_score / successful_scores, 1)
            logger.info(
                f"Average score from {len(judges)} judge agents: {average_answer_score}"
            )
        else:
            average_answer_score = None
            logger.warning(f"All {len(judges)} judges failed to parse score for document {seq_index}")
        scores.append(average_answer_score)

    return JudgementData(
        judgements=judgements,
        scores=scores,
        token_usage=judges_token_usage,
        elapsed=judges_elapsed,
    )
