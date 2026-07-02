import logging

from agent_enums import Role, Assignment

from agent.agent import Agent
from llm.token_usage import create_token_usage

logger = logging.getLogger(__name__)


async def correct_result(
    correctors: list[Agent], answers: list[str], role: Role
) -> dict:
    new_answers = []
    correctors_token_usage = create_token_usage()
    correctors_elapsed = 0

    for answer_index, answer in enumerate(answers, start=1):
        result = {"new_answer": answer}
        for index, corrector in enumerate(correctors, start=1):
            logger.info(
                f"Corrector {index}: correction of document {answer_index} is starting..."
            )
            result = await _correct_answer(corrector, result["new_answer"], role)
            logger.info(
                f"Corrector {index}: correction of document {answer_index} is completed"
            )

            token_usage = result["token_usage"]
            correctors_token_usage.add_usage(token_usage)
            correctors_elapsed += result["elapsed"]

        new_answers.append(result["new_answer"])

    return {
        "answers": new_answers,
        "correctors_token_usage": correctors_token_usage,
        "correctors_elapsed": correctors_elapsed,
    }


async def _correct_answer(corrector: Agent, answer: str, role: Role) -> dict:
    result = await corrector.analyze_doc(
        resources=[answer], role=role, assignment=Assignment.CORRECTOR
    )
    return {
        "new_answer": result["answer"],
        "token_usage": result["token_usage"],
        "elapsed": result["elapsed"],
    }
