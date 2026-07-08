import textwrap

from agent_enums import Mode, Role, Assignment, PromptType


DEFAULT_USER_PROMPTS_CHAT_ANY_ANY = [
    {
        "mode": Mode.CHAT.value,
        "role": Role.NOT_APPLICABLE.value,
        "assignment": Assignment.NOT_APPLICABLE.value,
        "prompt_type": PromptType.USER.value,
        "content": textwrap.dedent(
            """
            {init_user_prompt}
            Ниже приводится история предыдущих сообщений, учитывай этот контекст при формировании ответа на текущий запрос:
            {history}
            """
        ).strip(),
    },
]
