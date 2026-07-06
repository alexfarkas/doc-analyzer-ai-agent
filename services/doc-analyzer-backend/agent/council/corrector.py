import asyncio
import logging

from agent_enums import Role, Assignment

from agent.agent import Agent
from agent.models.agent_analysis_data import AgentAnalysisData
from agent.models.correction_data import CorrectionData
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

    async def run_corrector(
        corrector: Agent,
        in_q: asyncio.Queue,
        out_q: asyncio.Queue,
        is_last: bool,
    ):
        nonlocal correctors_token_usage, correctors_elapsed

        if progress_callback:
            await progress_callback(
                "agent_start",
                {
                    "agentId": corrector.agent_id,
                    "agentType": "corrector",
                },
            )

        try:
            while True:
                item = await in_q.get()

                if item is None:
                    if not is_last:
                        await out_q.put(None)
                    break

                idx, answer, seq = item
                logger.info(
                    f"Agent {corrector.agent_id} (corrector): correction of document {idx + 1} is starting..."
                )
                result = await _correct_answer(corrector, answer, role)

                new_answer_seq = result.answer_seq

                new_answer_item = new_answer_seq.answers[0]
                new_answer_item.author = "corrector"
                new_answer_item.status = "pre_correct"
                new_answer_item.init_status = "pre_correct"

                logger.info(
                    f"Agent {corrector.agent_id} (corrector): correction of document {idx + 1} is completed"
                )

                async with elapsed_lock:
                    correctors_token_usage.add_usage(result.token_usage)
                    correctors_elapsed += result.elapsed

                seq.answers.append(new_answer_item)
                await out_q.put((idx, new_answer_item.answer, seq))

        except Exception as e:
            logger.error(f"Agent {corrector.agent_id} (corrector) error: {e}", exc_info=True)
            if not is_last:
                try:
                    await out_q.put(None)
                except Exception as e:
                    pass
            raise
        finally:
            if progress_callback:
                await progress_callback(
                    "agent_end",
                    {
                        "agentId": corrector.agent_id,
                        "agentType": "corrector",
                    },
                )

    tasks = []
    for i, corrector in enumerate(correctors):
        is_last = i == len(correctors) - 1
        task = asyncio.create_task(
            run_corrector(corrector, queues[i], queues[i + 1], is_last)
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


async def _correct_answer(corrector: Agent, answer: str, role: Role) -> AgentAnalysisData:
    return await corrector.analyze_doc(
        resources=[answer], role=role, assignment=Assignment.CORRECTOR
    )
