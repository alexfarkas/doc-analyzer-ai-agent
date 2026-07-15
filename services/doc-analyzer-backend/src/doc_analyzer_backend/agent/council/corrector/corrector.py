import asyncio
import logging

from agent_enums import Role, Assignment, AnswerStatus

from src.doc_analyzer_backend.agent.agent import Agent
from src.doc_analyzer_backend.agent.models.council_assignments.correction_data import (
    CorrectionData,
)
from src.doc_analyzer_backend.agent.runners.council_agent_queue_runner import (
    run_agent_queue,
)

logger = logging.getLogger(__name__)


async def correct_result(
    correctors: list[Agent],
    role: Role,
    correction_data: CorrectionData,
    progress_callback=None,
) -> CorrectionData:
    elapsed_lock = asyncio.Lock()

    answer_seqs = correction_data.answer_seqs

    for seq in answer_seqs:
        for item in seq.answers:
            item.status = AnswerStatus.PRE_CORRECT
            item.init_status = AnswerStatus.PRE_CORRECT

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
                answer_status=AnswerStatus.PRE_CORRECT,
                in_q=queues[i],
                out_q=queues[i + 1],
                is_last=is_last,
                elapsed_lock=elapsed_lock,
                correction_data=correction_data,
                progress_callback=progress_callback,
            )
        )
        tasks.append(task)

    await asyncio.gather(*tasks)

    for seq in answer_seqs:
        if seq.answers:
            last_item = seq.answers[-1]
            last_item.status = AnswerStatus.FINAL
            last_item.init_status = AnswerStatus.FINAL

    return correction_data
