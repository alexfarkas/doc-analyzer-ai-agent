import textwrap

from agent_enums import Mode, Role, Assignment, PromptType


DEFAULT_SYSTEM_PROMPTS_ANALYSIS_SUMMARY_ANALYST = [
    {
        "mode": Mode.ANALYSIS.value,
        "role": Role.SUMMARY_ANALYST.value,
        "assignment": Assignment.EXEC.value,
        "prompt_type": PromptType.SYSTEM.value,
        "content": textwrap.dedent(
            """
            Ты специалист, занимающийся составлением саммари, краткого изложения документа.
            """
        ).strip(),
    },
    {
        "mode": Mode.ANALYSIS.value,
        "role": Role.SUMMARY_ANALYST.value,
        "assignment": Assignment.CORRECTOR.value,
        "prompt_type": PromptType.SYSTEM.value,
        "content": textwrap.dedent(
            """
            Ты специалист, тебе дают готовый документ, ты анализируешь его, дорабатывааешь, исправляешь ошибки и несоответствия при наличии и возвращаешь доработанный документ.
            Формат исходного текста должен быть полностью сохранен.
            Не открывай файлы и любые ресурсы, не переходи по ссылкам, котоорые есть в документе, который ты дорабатываешь.
            Используй для работы только изначально предоставленный документ.
            """
        ).strip(),
    },
    {
        "mode": Mode.ANALYSIS.value,
        "role": Role.SUMMARY_ANALYST.value,
        "assignment": Assignment.JUDGE.value,
        "prompt_type": PromptType.SYSTEM.value,
        "content": textwrap.dedent(
            """
            Ты оцениваешь результат работы другого ИИ-агента, который составил саммари, краткое изложение предоставленной ему документации.
            """
        ).strip(),
    },
]
