import textwrap

from agent_enums import Mode, Role, Assignment, PromptType


DEFAULT_SYSTEM_PROMPTS_CLARIFICATION_ANY_ANY = [
    {
        "mode": Mode.CLARIFICATION.value,
        "role": Role.NOT_APPLICABLE.value,
        "assignment": Assignment.NOT_APPLICABLE.value,
        "prompt_type": PromptType.SYSTEM.value,
        "content": textwrap.dedent(
            """
            {init_system_prompt}
            Тебе отправили текст и сообщение к нему. Ты должен переработать текст в соответствии с полученным сообщением. 
            """
        ).strip(),
    },
]
