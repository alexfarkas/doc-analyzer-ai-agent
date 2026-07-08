from src.doc_analyzer_backend.scripts.data.default_system_prompts import (
    DEFAULT_SYSTEM_PROMPTS_ANALYSIS_SUMMARY_ANALYST,
    DEFAULT_SYSTEM_PROMPTS_ANALYSIS_TECH_ANALYST,
    DEFAULT_SYSTEM_PROMPTS_ANALYSIS_CODE_REVIEWER,
    DEFAULT_SYSTEM_PROMPTS_ANALYSIS_TEACHER,
    DEFAULT_SYSTEM_PROMPTS_CHAT_ANY_ANY,
    DEFAULT_SYSTEM_PROMPTS_CLARIFICATION_ANY_ANY,
)


def system_prompt_analysis_summary_analyst_exec() -> str:
    return DEFAULT_SYSTEM_PROMPTS_ANALYSIS_SUMMARY_ANALYST[0]["content"]


def system_prompt_analysis_summary_analyst_corrector() -> str:
    return DEFAULT_SYSTEM_PROMPTS_ANALYSIS_SUMMARY_ANALYST[1]["content"]


def system_prompt_analysis_summary_analyst_judge() -> str:
    return DEFAULT_SYSTEM_PROMPTS_ANALYSIS_SUMMARY_ANALYST[2]["content"]


def system_prompt_analysis_tech_analyst_exec() -> str:
    return DEFAULT_SYSTEM_PROMPTS_ANALYSIS_TECH_ANALYST[0]["content"]


def system_prompt_analysis_tech_analyst_corrector() -> str:
    return DEFAULT_SYSTEM_PROMPTS_ANALYSIS_TECH_ANALYST[1]["content"]


def system_prompt_analysis_tech_analyst_judge() -> str:
    return DEFAULT_SYSTEM_PROMPTS_ANALYSIS_TECH_ANALYST[2]["content"]


def system_prompt_analysis_code_reviewer_exec() -> str:
    return DEFAULT_SYSTEM_PROMPTS_ANALYSIS_CODE_REVIEWER[0]["content"]


def system_prompt_analysis_code_reviewer_corrector() -> str:
    return DEFAULT_SYSTEM_PROMPTS_ANALYSIS_CODE_REVIEWER[1]["content"]


def system_prompt_analysis_code_reviewer_judge() -> str:
    return DEFAULT_SYSTEM_PROMPTS_ANALYSIS_CODE_REVIEWER[2]["content"]


def system_prompt_analysis_teacher_exec() -> str:
    return DEFAULT_SYSTEM_PROMPTS_ANALYSIS_TEACHER[0]["content"]


def system_prompt_analysis_teacher_corrector() -> str:
    return DEFAULT_SYSTEM_PROMPTS_ANALYSIS_TEACHER[1]["content"]


def system_prompt_analysis_teacher_judge() -> str:
    return DEFAULT_SYSTEM_PROMPTS_ANALYSIS_TEACHER[2]["content"]


def system_prompt_clarification_any_any(**kwargs):
    return DEFAULT_SYSTEM_PROMPTS_CLARIFICATION_ANY_ANY[0]["content"].format(
        init_system_prompt=kwargs.get("init_system_prompt", None)
    )


def system_prompt_chat_any_any(**kwargs):
    return DEFAULT_SYSTEM_PROMPTS_CHAT_ANY_ANY[0]["content"].format(
        init_system_prompt=kwargs.get("init_system_prompt", None)
    )
