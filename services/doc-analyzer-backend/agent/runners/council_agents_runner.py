import logging
from typing import Callable, Awaitable, Any

from agent_enums import Role

from agent.agent import Agent
from agent.models.agent_analysis_data import AgentAnalysisData
from llm.tokens.token_usage import TokenUsage

logger = logging.getLogger(__name__)


async def run_agent(
    agent: Agent,
    role: Role,
    resources: list[str],
    progress_callback=None,
) -> AgentAnalysisData:
    if progress_callback:
        await progress_callback(
            "agent_start",
            {
                "agentId": agent.agent_id,
                "agentType": "exec",
            },
        )
    logger.info(f"Agent {agent.agent_id} (exec): doc analysis is starting...")
    try:
        return await agent.analyze_doc(resources=resources, role=role)
    finally:
        logger.info(f"Agent {agent.agent_id} (exec): doc analysis is completed")
        if progress_callback:
            await progress_callback(
                "agent_end",
                {
                    "agentId": agent.agent_id,
                    "agentType": "exec",
                },
            )


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
