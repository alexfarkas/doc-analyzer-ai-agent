from agent_enums import Assignment, AnswerStatus

from src.doc_analyzer_backend.api.models.analisys.answer_item import AnswerItem
from src.doc_analyzer_backend.api.models.analisys.answer_seq import AnswerSeq
from tests.consts.agent import DEFAULT_ANSWER, DEFAULT_ASSIGNMENT, DEFAULT_STATUS


def make_answer_item(
    answer: str = DEFAULT_ANSWER,
    author: Assignment = DEFAULT_ASSIGNMENT,
    status: AnswerStatus = DEFAULT_STATUS,
    init_status: AnswerStatus = DEFAULT_STATUS,
) -> AnswerItem:
    """Single answer_item block for agent mock"""
    return AnswerItem(
        answer=answer,
        author=author,
        status=status,
        init_status=init_status,
    )


def make_answer_seq(
    answers: list[AnswerItem] | None = None,
    answers_count: int | None = None,
) -> AnswerSeq:
    """Single answer_seq block for agent mock"""
    if answers:
        return AnswerSeq(answers=answers)
    elif answers_count:
        return AnswerSeq(
            answers=[
                make_answer_item(answer=f"{DEFAULT_ANSWER} {i}")
                for i in range(answers_count)
            ]
        )
    else:
        return AnswerSeq(answers=[make_answer_item(answer=DEFAULT_ANSWER)])
