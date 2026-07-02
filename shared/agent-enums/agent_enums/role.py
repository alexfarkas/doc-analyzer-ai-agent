from enum import Enum


class Role(str, Enum):
    SUMMARY_ANALYST = "summary_analyst"
    TECH_ANALYST = "tech_analyst"
    CODE_REVIEWER = "code_reviewer"
    TEACHER = "teacher"
    NOT_APPLICABLE = "not_applicable"
