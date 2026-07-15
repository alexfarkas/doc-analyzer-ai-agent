import logging

from agent_enums import Role

from src.doc_analyzer_backend.agent.agent import Agent
from src.doc_analyzer_backend.agent.council.judge.doc_judge import judge_document
from src.doc_analyzer_backend.agent.council.judge.judge_runner import run_judges_async
from src.doc_analyzer_backend.agent.council.judge.score_counter import count_scores
from src.doc_analyzer_backend.agent.models.consumption_data import create_consumption_data
from src.doc_analyzer_backend.agent.models.judgement_data import JudgementData
from src.doc_analyzer_backend.api.models.analisys.answer_seq import AnswerSeq

logger = logging.getLogger(__name__)


async def judge_result(
    judges: list[Agent],
    answer_seqs: list[AnswerSeq],
    role: Role,
    progress_callback=None,
) -> JudgementData:
    judgements = []
    scores = []
    consumption_data = create_consumption_data()

    for seq_index, seq in enumerate(answer_seqs, start=1):
        logger.info(f"Judgment for document {seq_index} is starting...")

        results = await run_judges_async(
            judges=judges,
            last_answer=seq.answers[-1].answer,
            role=role,
            progress_callback=progress_callback,
            doc_index=seq_index,
        )

        doc_judgement = await judge_document(results=results)

        logger.info(f"Judgement for document {seq_index} is completed")

        judgements.append(
            "\n\n".join(
                f"Судья {i + 1}:\n\n{j}" for i, j in enumerate(doc_judgement.answer_judgements)
            )
        )
        consumption_data.update_by_data(doc_judgement.consumption_data)
        scores.append(
            await count_scores(doc_judgement=doc_judgement, doc_index=seq_index)
        )

    return JudgementData(
        judgements=judgements,
        scores=scores,
        consumption_data=consumption_data,
    )
