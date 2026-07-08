import logging
from typing import Sequence

from agent_enums import Mode
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

logger = logging.getLogger(__name__)


def build_messages(prompts: tuple[str, str], mode: Mode) -> list[BaseMessage]:
    system_prompt, user_prompt = prompts

    logger.debug(f"System {mode.value} prompt: {system_prompt}")
    logger.debug(f"User {mode.value} prompt: {user_prompt}")

    return [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]


async def extract_final_answer(messages: Sequence[BaseMessage]) -> str:
    final_msg = next(
        (m.content for m in reversed(messages) if m.type == "ai"),
        "No answer from agent",
    )

    logger.debug(f"Answer from model: {final_msg}")

    return final_msg
