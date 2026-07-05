import logging

from data.app_state_manager import app_state
from llm.token_usage import TokenUsage

logger = logging.getLogger(__name__)


async def update_and_get_total_token_usage(
    token_usage: TokenUsage,
) -> TokenUsage:
    await app_state.add_token_usage(token_usage)
    total_token_usage = await app_state.get_token_usage()
    logger.info(f"Total token usage: {total_token_usage}")
    return total_token_usage
