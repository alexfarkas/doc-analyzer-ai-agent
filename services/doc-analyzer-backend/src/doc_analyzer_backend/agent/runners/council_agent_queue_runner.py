import asyncio
import logging

from agent_enums import Role, Assignment, AnswerStatus

from src.doc_analyzer_backend.agent.agent import Agent
from src.doc_analyzer_backend.agent.messages_data.progress_data import start_event, stop_event
from src.doc_analyzer_backend.agent.models.agent_analysis_data import AgentAnalysisData
from src.doc_analyzer_backend.llm.tokens.token_usage import TokenUsage

logger = logging.getLogger(__name__)


async def run_agent_queue(
    agent: Agent,
    role: Role,
    assignment: Assignment,
    answer_status: AnswerStatus,
    in_q: asyncio.Queue,
    out_q: asyncio.Queue,
    is_last: bool,
    elapsed_lock: asyncio.Lock,
    token_usage: TokenUsage,
    elapsed: float,
    progress_callback=None,
):
    if progress_callback:
        await progress_callback(start_event(agent.agent_id, assignment))

    try:
        while True:
            item = await in_q.get()

            if item is None:
                if not is_last:
                    await out_q.put(None)
                break

            idx, answer, seq = item
            logger.info(
                f"Agent {agent.agent_id} ({assignment.value}): processing of document {idx + 1} is starting..."
            )
            result = await _analyse_answer(
                agent=agent,
                answer=answer,
                role=role,
                assignment=assignment,
            )

            new_answer_item = result.answer_item
            new_answer_item.author = assignment
            new_answer_item.status = answer_status
            new_answer_item.init_status = answer_status

            logger.info(
                f"Agent {agent.agent_id} ({assignment.value}): processing of document {idx + 1} is completed"
            )

            async with elapsed_lock:
                token_usage.add_usage(result.token_usage)
                elapsed += result.elapsed

            seq.answers.append(new_answer_item)
            await out_q.put((idx, new_answer_item.answer, seq))

    except Exception as e:
        logger.error(
            f"Agent {agent.agent_id} ({assignment.value}) error: {e}", exc_info=True
        )
        if not is_last:
            try:
                await out_q.put(None)
            except Exception as e:
                pass
        raise
    finally:
        if progress_callback:
            await progress_callback(stop_event(agent.agent_id, assignment))


async def _analyse_answer(
    agent: Agent,
    answer: str,
    role: Role,
    assignment: Assignment,
) -> AgentAnalysisData:
    return await agent.analyze_doc(
        resources=[answer],
        role=role,
        assignment=assignment,
    )
