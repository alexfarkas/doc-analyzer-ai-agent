from agent_enums import Assignment, Mode, Role, PromptType
from db_repository import PromptRepository

from local_prompts.system_prompts import (
    system_prompt_analysis_summary_analyst_exec,
    system_prompt_analysis_tech_analyst_exec,
    system_prompt_analysis_code_reviewer_exec,
    system_prompt_analysis_teacher_exec,
    system_prompt_analysis_summary_analyst_corrector,
    system_prompt_analysis_tech_analyst_corrector,
    system_prompt_analysis_code_reviewer_corrector,
    system_prompt_analysis_teacher_corrector,
    system_prompt_analysis_summary_analyst_judge,
    system_prompt_analysis_tech_analyst_judge,
    system_prompt_analysis_code_reviewer_judge,
    system_prompt_analysis_teacher_judge,
    system_prompt_clarification_any_any,
    system_prompt_chat_any_any,
)
from local_prompts.user_prompts import (
    user_prompt_analysis_summary_analyst_exec,
    user_prompt_analysis_tech_analyst_exec,
    user_prompt_analysis_code_reviewer_exec,
    user_prompt_analysis_teacher_exec,
    user_prompt_analysis_summary_analyst_corrector,
    user_prompt_analysis_tech_analyst_corrector,
    user_prompt_analysis_code_reviewer_corrector,
    user_prompt_analysis_teacher_corrector,
    user_prompt_analysis_summary_analyst_judge,
    user_prompt_analysis_tech_analyst_judge,
    user_prompt_analysis_code_reviewer_judge,
    user_prompt_analysis_teacher_judge,
    user_prompt_clarification_any_any,
    user_prompt_chat_any_any,
)


async def get_prompts(
    mode: Mode,
    role: Role = Role.NOT_APPLICABLE,
    assignment: Assignment = Assignment.NOT_APPLICABLE,
    prompt_repository: PromptRepository | None = None,
    **kwargs,
) -> tuple[str, str]:
    if prompt_repository:
        return await _get_db_prompts(
            prompt_repository, mode, role, assignment, **kwargs
        )
    else:
        return await _get_local_prompts(mode, role, assignment, **kwargs)


async def _get_db_prompts(
    prompt_repository: PromptRepository,
    mode: Mode,
    role: Role,
    assignment: Assignment = Assignment.EXEC,
    **kwargs,
):
    system_prompt = prompt_repository.get_prompt_with_format(
        mode=mode, role=role, assignment=assignment, prompt_type=PromptType.SYSTEM
    )
    user_prompt = prompt_repository.get_prompt_with_format(
        mode=mode,
        role=role,
        assignment=assignment,
        prompt_type=PromptType.USER,
        **kwargs,
    )

    if not system_prompt or not user_prompt:
        raise ValueError(
            f"Prompts not found for mode: {mode.value}, role: {role.value} and assignment: {assignment.value}"
        )

    return system_prompt, user_prompt


async def _get_local_prompts(
    mode: Mode, role: Role, assignment: Assignment, **kwargs
) -> tuple[str, str]:
    match mode:
        case Mode.ANALYSIS:
            return await _get_local_prompts_analysis(role, assignment, **kwargs)
        case Mode.CLARIFICATION:
            return await _get_local_prompts_clarification(role, assignment, **kwargs)
        case Mode.CHAT:
            return await _get_local_prompts_chat(role, assignment, **kwargs)
        case _:
            raise ValueError(f"Unknown agent mode: {mode}")


async def _get_local_prompts_analysis(
    role: Role, assignment: Assignment, **kwargs
) -> tuple[str, str]:
    match role:
        case Role.SUMMARY_ANALYST:
            return await _get_local_prompts_summary_analyst(assignment, **kwargs)
        case Role.TECH_ANALYST:
            return await _get_local_prompts_tech_analyst(assignment, **kwargs)
        case Role.CODE_REVIEWER:
            return await _get_local_prompts_code_review(assignment, **kwargs)
        case Role.TEACHER:
            return await _get_local_prompts_teacher(assignment, **kwargs)
        case _:
            raise ValueError(f"Unknown agent role: {role}")


async def _get_local_prompts_clarification(
    role: Role, assignment: Assignment, **kwargs
) -> tuple[str, str]:
    return (
        system_prompt_clarification_any_any(**kwargs),
        user_prompt_clarification_any_any(**kwargs),
    )


async def _get_local_prompts_chat(
    role: Role, assignment: Assignment, **kwargs
) -> tuple[str, str]:
    return (system_prompt_chat_any_any(**kwargs), user_prompt_chat_any_any(**kwargs))


async def _get_local_prompts_summary_analyst(
    assignment: Assignment, **kwargs
) -> tuple[str, str]:
    match assignment:
        case Assignment.EXEC:
            return (
                system_prompt_analysis_summary_analyst_exec(),
                user_prompt_analysis_summary_analyst_exec(**kwargs),
            )
        case Assignment.CORRECTOR:
            return (
                system_prompt_analysis_summary_analyst_corrector(),
                user_prompt_analysis_summary_analyst_corrector(**kwargs),
            )
        case Assignment.JUDGE:
            return (
                system_prompt_analysis_summary_analyst_judge(),
                user_prompt_analysis_summary_analyst_judge(**kwargs),
            )
        case _:
            raise ValueError(f"Unknown agent assignment: {assignment}")


async def _get_local_prompts_tech_analyst(
    assignment: Assignment, **kwargs
) -> tuple[str, str]:
    match assignment:
        case Assignment.EXEC:
            return (
                system_prompt_analysis_tech_analyst_exec(),
                user_prompt_analysis_tech_analyst_exec(**kwargs),
            )
        case Assignment.CORRECTOR:
            return (
                system_prompt_analysis_tech_analyst_corrector(),
                user_prompt_analysis_tech_analyst_corrector(**kwargs),
            )
        case Assignment.JUDGE:
            return (
                system_prompt_analysis_tech_analyst_judge(),
                user_prompt_analysis_tech_analyst_judge(**kwargs),
            )
        case _:
            raise ValueError(f"Unknown agent assignment: {assignment}")


async def _get_local_prompts_code_review(
    assignment: Assignment, **kwargs
) -> tuple[str, str]:
    match assignment:
        case Assignment.EXEC:
            return (
                system_prompt_analysis_code_reviewer_exec(),
                user_prompt_analysis_code_reviewer_exec(**kwargs),
            )
        case Assignment.CORRECTOR:
            return (
                system_prompt_analysis_code_reviewer_corrector(),
                user_prompt_analysis_code_reviewer_corrector(**kwargs),
            )
        case Assignment.JUDGE:
            return (
                system_prompt_analysis_code_reviewer_judge(),
                user_prompt_analysis_code_reviewer_judge(**kwargs),
            )
        case _:
            raise ValueError(f"Unknown agent assignment: {assignment}")


async def _get_local_prompts_teacher(
    assignment: Assignment, **kwargs
) -> tuple[str, str]:
    match assignment:
        case Assignment.EXEC:
            return (
                system_prompt_analysis_teacher_exec(),
                user_prompt_analysis_teacher_exec(**kwargs),
            )
        case Assignment.CORRECTOR:
            return (
                system_prompt_analysis_teacher_corrector(),
                user_prompt_analysis_teacher_corrector(**kwargs),
            )
        case Assignment.JUDGE:
            return (
                system_prompt_analysis_teacher_judge(),
                user_prompt_analysis_teacher_judge(**kwargs),
            )
        case _:
            raise ValueError(f"Unknown agent assignment: {assignment}")
