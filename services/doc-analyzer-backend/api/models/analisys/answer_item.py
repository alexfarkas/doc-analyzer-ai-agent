from agent_enums import Assignment, AnswerStatus
from pydantic import BaseModel


class AnswerItem(BaseModel):
    answer: str
    author: Assignment
    status: AnswerStatus
    init_status: AnswerStatus
