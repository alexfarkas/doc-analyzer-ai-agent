import logging

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

logger = logging.getLogger(__name__)


class ConversationHistory:
    def __init__(self):
        self._storage: list[BaseMessage] = []
        self.system_prompt = ""

    def get_all(self):
        return self._storage

    def get_last_messages(self, count: int) -> list[BaseMessage]:
        logger.info(f"Retrieve {count} last messages from history")
        return self._storage[-count:]

    def save(self, messages: tuple[str, str]):
        logger.info("Save prompts to history")
        system_prompt, user_prompt = messages

        self.system_prompt = system_prompt

        self.save_system_prompt(system_prompt)
        self.save_user_prompt(user_prompt)

    def save_system_prompt(self, message: str):
        logger.info("Save system prompt to history")
        self._storage.append(SystemMessage(content=message))

    def save_user_prompt(self, message: str):
        logger.info("Save user prompt to history")
        self._storage.append(HumanMessage(content=message))

    def save_ai_message(self, message: str):
        logger.info("Save AI answer to history")
        self._storage.append(AIMessage(content=message))

    def trim(self, max_turns: int = 5):
        logger.info("Trimming history...")
        if len(self._storage) <= max_turns * 2 + 1:
            logger.info("No need for history trimming")
            return

        sys_idx = next(
            (i for i, m in enumerate(self._storage) if isinstance(m, SystemMessage)),
            None,
        )

        keep_count = max_turns * 2
        trimmed = self._storage[-keep_count:]
        if sys_idx is not None and not any(
            isinstance(m, SystemMessage) for m in trimmed
        ):
            trimmed.insert(0, self._storage[sys_idx])

        self._storage = trimmed
        logger.info("History trimmed")

    def as_string(self) -> str:
        return "\n\n".join([f"{m.type}:\n{m.content}" for m in self._storage])

    def clear(self):
        logger.info("Clear history")
        self._storage = []
