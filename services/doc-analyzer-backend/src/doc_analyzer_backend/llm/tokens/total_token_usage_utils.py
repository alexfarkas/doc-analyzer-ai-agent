import logging

from src.doc_analyzer_backend.data.app_state_manager import app_state
from src.doc_analyzer_backend.llm.tokens.token_usage import TokenUsage

logger = logging.getLogger(__name__)


async def update_and_get_total_token_usage(
    token_usage: TokenUsage | None,
) -> TokenUsage:
    await app_state.add_token_usage(token_usage)
    total_token_usage = await app_state.get_token_usage()
    logger.info(f"Total token usage: {total_token_usage}")
    return total_token_usage
