from pydantic import BaseModel

from api.models.analisys.answer_item import AnswerItem


class AnswerSeq(BaseModel):
    answers: list[AnswerItem]


def create_answer_seq(item: AnswerItem) -> AnswerSeq:
    return AnswerSeq(answers=[item])
