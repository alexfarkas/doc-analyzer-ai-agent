import logging
from typing import Callable, Awaitable, Any

from src.doc_analyzer_backend.agent.models.consumption_data import ConsumptionData

logger = logging.getLogger(__name__)


async def run_stage(
    stage_name: str,
    stage_fn: Callable[[], Awaitable],
    consumption_data: ConsumptionData,
) -> tuple[Any, ConsumptionData]:
    logger.info(f"Running {stage_name} stage")

    result = await stage_fn()
    consumption_data.update_by_data(result.consumption_data)

    return result, consumption_data
