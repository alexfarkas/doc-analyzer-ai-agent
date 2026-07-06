from pydantic import BaseModel

from api.models.analisys.answer_item import AnswerItem
from llm.tokens.token_usage import TokenUsage


class AgentAnalysisData(BaseModel):
    answer_item: AnswerItem
    token_usage: TokenUsage | None = None
    elapsed: float
    cost_rub: float = 0
