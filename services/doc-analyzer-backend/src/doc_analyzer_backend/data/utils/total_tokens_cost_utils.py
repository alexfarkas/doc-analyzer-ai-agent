import logging

from src.doc_analyzer_backend.agent.models.tokens.consumption_data import (
    ConsumptionData,
)
from src.doc_analyzer_backend.data.app_state_manager import app_state
from src.doc_analyzer_backend.agent.models.tokens.token_usage import TokenUsage

logger = logging.getLogger(__name__)


async def update_total_consumption(
    consumption_data: ConsumptionData,
) -> tuple[TokenUsage, float]:
    logger.info(f"Updating total consumption in app data with: {consumption_data}")

    await app_state.add_token_usage(consumption_data.token_usage)
    await app_state.add_cost(consumption_data.cost)

    total_token_usage = await app_state.get_token_usage()
    total_cost = await app_state.get_cost()

    logger.info(f"Total token usage: {total_token_usage}")
    logger.info(f"Total cost: {total_cost}")

    return total_token_usage, total_cost
