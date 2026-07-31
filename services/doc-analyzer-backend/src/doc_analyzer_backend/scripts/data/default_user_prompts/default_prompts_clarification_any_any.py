import textwrap

from agent_enums import Mode, Role, Assignment, PromptType


DEFAULT_USER_PROMPTS_CLARIFICATION_ANY_ANY = [
    {
        "mode": Mode.CLARIFICATION.value,
        "role": Role.NOT_APPLICABLE.value,
        "assignment": Assignment.NOT_APPLICABLE.value,
        "prompt_type": PromptType.USER.value,
        "content": textwrap.dedent(
            """
            Первоначальный текст выглядит так:
            {clarifying_answer}
            
            Задача: переработай первоначальный текст в соответствии с тем, что описано в сообщении:
            {init_user_prompt} 
            
            Формат ответа:
            Ты должен сформировать полностью готовый текст, переработанный на основе сообщения.
            В ответе верни исправленный текст в том же формате, что и изначальный.
            ВАЖНО: сформируй полностью готовый результат сразу и верни его на первой же итерации.
            """
        ).strip(),
    },
]
