import textwrap

from agent_enums import Mode, Role, Assignment, PromptType


DEFAULT_SYSTEM_PROMPTS_CHAT_ANY_ANY = [
    {
        "mode": Mode.CHAT.value,
        "role": Role.NOT_APPLICABLE.value,
        "assignment": Assignment.NOT_APPLICABLE.value,
        "prompt_type": PromptType.SYSTEM.value,
        "content": textwrap.dedent(
            """
            {init_system_prompt}
            Тебе отправили сообщение. Ты должен ответить в констексте истории беседы.
            """
        ).strip(),
    },
]
