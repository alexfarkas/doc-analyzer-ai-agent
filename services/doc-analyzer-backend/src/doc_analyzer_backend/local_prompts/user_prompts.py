from src.doc_analyzer_backend.scripts.data.default_user_prompts import (
    DEFAULT_USER_PROMPTS_ANALYSIS_SUMMARY_ANALYST,
    DEFAULT_USER_PROMPTS_ANALYSIS_TECH_ANALYST,
    DEFAULT_USER_PROMPTS_ANALYSIS_CODE_REVIEWER,
    DEFAULT_USER_PROMPTS_ANALYSIS_TEACHER,
    DEFAULT_USER_PROMPTS_CHAT_ANY_ANY,
    DEFAULT_USER_PROMPTS_CLARIFICATION_ANY_ANY,
)


def user_prompt_analysis_summary_analyst_exec(**kwargs) -> str:
    return DEFAULT_USER_PROMPTS_ANALYSIS_SUMMARY_ANALYST[0]["content"].format(
        resources=kwargs.get("resources", None)
    )


def user_prompt_analysis_summary_analyst_corrector(**kwargs) -> str:
    return DEFAULT_USER_PROMPTS_ANALYSIS_SUMMARY_ANALYST[1]["content"].format(
        resources=kwargs.get("resources", None)
    )


def user_prompt_analysis_summary_analyst_judge(**kwargs) -> str:
    return DEFAULT_USER_PROMPTS_ANALYSIS_SUMMARY_ANALYST[2]["content"].format(
        resources=kwargs.get("resources", None)
    )


def user_prompt_analysis_tech_analyst_exec(**kwargs) -> str:
    return DEFAULT_USER_PROMPTS_ANALYSIS_TECH_ANALYST[0]["content"].format(
        resources=kwargs.get("resources", None)
    )


def user_prompt_analysis_tech_analyst_corrector(**kwargs) -> str:
    return DEFAULT_USER_PROMPTS_ANALYSIS_TECH_ANALYST[1]["content"].format(
        resources=kwargs.get("resources", None)
    )


def user_prompt_analysis_tech_analyst_judge(**kwargs) -> str:
    return DEFAULT_USER_PROMPTS_ANALYSIS_TECH_ANALYST[2]["content"].format(
        resources=kwargs.get("resources", None)
    )


def user_prompt_analysis_code_reviewer_exec(**kwargs) -> str:
    return DEFAULT_USER_PROMPTS_ANALYSIS_CODE_REVIEWER[0]["content"].format(
        resources=kwargs.get("resources", None)
    )


def user_prompt_analysis_code_reviewer_corrector(**kwargs) -> str:
    return DEFAULT_USER_PROMPTS_ANALYSIS_CODE_REVIEWER[1]["content"].format(
        resources=kwargs.get("resources", None)
    )


def user_prompt_analysis_code_reviewer_judge(**kwargs) -> str:
    return DEFAULT_USER_PROMPTS_ANALYSIS_CODE_REVIEWER[2]["content"].format(
        resources=kwargs.get("resources", None)
    )


def user_prompt_analysis_teacher_exec(**kwargs) -> str:
    return DEFAULT_USER_PROMPTS_ANALYSIS_TEACHER[0]["content"].format(
        resources=kwargs.get("resources", None)
    )


def user_prompt_analysis_teacher_corrector(**kwargs) -> str:
    return DEFAULT_USER_PROMPTS_ANALYSIS_TEACHER[1]["content"].format(
        resources=kwargs.get("resources", None)
    )


def user_prompt_analysis_teacher_judge(**kwargs) -> str:
    return DEFAULT_USER_PROMPTS_ANALYSIS_TEACHER[2]["content"].format(
        resources=kwargs.get("resources", None)
    )


def user_prompt_clarification_any_any(**kwargs):
    return DEFAULT_USER_PROMPTS_CLARIFICATION_ANY_ANY[0]["content"].format(
        init_user_prompt=kwargs.get("init_user_prompt", None),
        ai_answer=kwargs.get("ai_answer", None),
    )


def user_prompt_chat_any_any(**kwargs):
    return DEFAULT_USER_PROMPTS_CHAT_ANY_ANY[0]["content"].format(
        init_user_prompt=kwargs.get("init_user_prompt", None),
        history=kwargs.get("history", None),
    )
