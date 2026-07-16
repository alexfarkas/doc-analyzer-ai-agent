import logging
import time

from langchain_core.messages import BaseMessage
from langgraph.graph.state import CompiledStateGraph

from src.doc_analyzer_backend.agent.consumption_counters.consumption_counter import calculate_consumption
from src.doc_analyzer_backend.agent.messages_data.messages_utils import extract_final_answer
from src.doc_analyzer_backend.agent.models.tokens.consumption_data import ConsumptionData
from src.doc_analyzer_backend.utils.truncate import truncate_value

logger = logging.getLogger(__name__)

async def ai_invoke_track(
    agent_id: int,
    app: CompiledStateGraph,
    messages: list[BaseMessage],
    provider: str,
    model: str,
    type_message: str,
) -> tuple[str, ConsumptionData]:
    start = time.perf_counter()
    logger.info(f"Agent {agent_id}: {type_message} is starting...")

    result = await app.ainvoke({"messages": messages})
    final_msg = await extract_final_answer(result["messages"])
    logger.debug(f"AI final message: {truncate_value(final_msg)}")

    elapsed = time.perf_counter() - start
    logger.info(
        f"Agent {agent_id}: {type_message} is completed in {elapsed} seconds"
    )

    consumption_data = calculate_consumption(
        agent_id=agent_id,
        messages=result["messages"],
        provider=provider,
        model=model,
        elapsed=elapsed,
    )

    return final_msg, consumption_data
