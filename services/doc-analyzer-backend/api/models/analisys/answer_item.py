from pydantic import BaseModel


class AnswerItem(BaseModel):
    answer: str
    author: str
    status: str
    init_status: str
