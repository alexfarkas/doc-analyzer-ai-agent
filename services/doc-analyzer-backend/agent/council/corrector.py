import asyncio
import logging

from agent_enums import Role, Assignment

from agent.agent import Agent
from agent.models.correction_data import CorrectionData
from agent.runners.council_agent_queue_runner import run_agent_queue
from api.models.analisys.answer_seq import AnswerSeq
from llm.tokens.token_usage import create_token_usage

logger = logging.getLogger(__name__)


async def correct_result(
    correctors: list[Agent],
    answer_seqs: list[AnswerSeq],
    role: Role,
    progress_callback=None,
) -> CorrectionData:
    correctors_token_usage = create_token_usage()
    correctors_elapsed = 0
    elapsed_lock = asyncio.Lock()

    for seq in answer_seqs:
        for item in seq.answers:
            item.status = "pre_correct"
            item.init_status = "pre_correct"

    input_queue = asyncio.Queue()
    queues = [input_queue]
    for _ in correctors:
        queues.append(asyncio.Queue())

    for idx, seq in enumerate(answer_seqs):
        current_item = seq.answers[-1]
        await input_queue.put((idx, current_item.answer, seq))
    await input_queue.put(None)

    tasks = []
    for i, corrector in enumerate(correctors):
        is_last = i == len(correctors) - 1
        task = asyncio.create_task(
            run_agent_queue(
                agent=corrector,
                role=role,
                assignment=Assignment.CORRECTOR,
                answer_status="pre_correct",
                in_q=queues[i],
                out_q=queues[i + 1],
                is_last=is_last,
                elapsed_lock=elapsed_lock,
                token_usage=correctors_token_usage,
                elapsed=correctors_elapsed,
                progress_callback=progress_callback,
            )
        )
        tasks.append(task)

    await asyncio.gather(*tasks)

    for seq in answer_seqs:
        if seq.answers:
            last_item = seq.answers[-1]
            last_item.status = "final"
            last_item.init_status = "final"

    return CorrectionData(
        answer_seqs=answer_seqs,
        token_usage=correctors_token_usage,
        elapsed=correctors_elapsed,
    )
