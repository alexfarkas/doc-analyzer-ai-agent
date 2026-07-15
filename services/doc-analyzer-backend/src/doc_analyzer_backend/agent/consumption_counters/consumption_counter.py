import logging

from langchain_core.messages import BaseMessage

from src.doc_analyzer_backend.agent.consumption_counters.cost_counter import calculate_cost
from src.doc_analyzer_backend.agent.consumption_counters.token_counter import calculate_token_usage
from src.doc_analyzer_backend.agent.models.tokens.consumption_data import create_consumption_data

logger = logging.getLogger(__name__)


DEFAULT_CURRENCY = "RUB"


def calculate_consumption(
    agent_id: int,
    messages: list[BaseMessage],
    provider: str,
    model: str,
    elapsed: float,
):
    token_usage = calculate_token_usage(
        messages=messages,
        provider=provider,
        model=model,
    )
    cost = calculate_cost(
        token_usage=token_usage,
        provider=provider,
        model=model,
        currency=DEFAULT_CURRENCY,
    )

    logger.info(f"Agent {agent_id} tokens usage: {token_usage}")
    logger.info(f"Agent {agent_id} cost: {cost}")

    return create_consumption_data(
        token_usage=token_usage,
        elapsed=elapsed,
        cost=cost,
    )
