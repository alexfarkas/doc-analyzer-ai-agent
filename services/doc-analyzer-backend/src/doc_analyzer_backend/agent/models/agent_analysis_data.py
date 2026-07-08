from pydantic import BaseModel

from src.doc_analyzer_backend.api.models.analisys.answer_item import AnswerItem
from src.doc_analyzer_backend.llm.tokens.token_usage import TokenUsage


class AgentAnalysisData(BaseModel):
    answer_item: AnswerItem
    token_usage: TokenUsage | None = None
    elapsed: float
    cost_rub: float = 0
