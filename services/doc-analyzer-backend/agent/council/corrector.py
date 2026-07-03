import asyncio
import logging

from agent_enums import Role, Assignment

from agent.agent import Agent
from llm.token_usage import create_token_usage

logger = logging.getLogger(__name__)


async def correct_result(
    correctors: list[Agent],
    answers: list[str],
    role: Role,
    progress_callback=None,
) -> dict:
    correctors_token_usage = create_token_usage()
    correctors_elapsed = 0
    elapsed_lock = asyncio.Lock()

    input_queue = asyncio.Queue()
    queues = [input_queue]
    for _ in correctors:
        queues.append(asyncio.Queue())

    for ids, answer in enumerate(answers):
        await input_queue.put((ids, answer))
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

                idx, answer = item
                logger.info(
                    f"Agent {corrector.agent_id} (corrector): correction of document {idx + 1} is starting..."
                )
                result = await _correct_answer(corrector, answer, role)
                logger.info(
                    f"Agent {corrector.agent_id} (corrector): correction of document {idx + 1} is completed"
                )

                async with elapsed_lock:
                    correctors_token_usage.add_usage(result["token_usage"])
                    correctors_elapsed += result["elapsed"]

                await out_q.put((idx, result["new_answer"]))

        except Exception as e:
            logger.error(f"Agent {corrector.agent_id} (corrector) error: {e}")
            if not is_last:
                await out_q.put(None)
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
        is_last = (i == len(correctors) - 1)
        task = asyncio.create_task(
            run_corrector(corrector, queues[i], queues[i + 1], is_last)
        )
        tasks.append(task)

    await asyncio.gather(*tasks)

    output_queue = queues[-1]
    results = []
    while True:
        try:
            results.append(output_queue.get_nowait())
        except asyncio.QueueEmpty:
            break

    results.sort(key=lambda x: x[0])
    new_answers = [answer for _, answer in results]

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
