import logging
from typing import Callable, Awaitable, Any

from src.doc_analyzer_backend.llm.tokens.token_usage import TokenUsage

logger = logging.getLogger(__name__)


async def run_stage(
    stage_name: str,
    stage_fn: Callable[[], Awaitable],
    council_token_usage: TokenUsage,
    total_elapsed: float,
) -> tuple[Any, float]:
    logger.info(f"{stage_name} is starting...")
    result = await stage_fn()
    logger.info(f"{stage_name} is completed")

    council_token_usage.add_usage(result.token_usage)
    total_elapsed += result.elapsed

    logger.info(f"{stage_name} token usage: {result.token_usage}")
    logger.info(f"Council token usage: {council_token_usage}")

    return result, total_elapsed
