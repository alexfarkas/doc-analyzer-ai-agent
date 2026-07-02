from enum import Enum


class Assignment(str, Enum):
    EXEC = "exec"
    JUDGE = "judge"
    CORRECTOR = "corrector"
    POST_CORRECTOR = "post_corrector"
    NOT_APPLICABLE = "not_applicable"
