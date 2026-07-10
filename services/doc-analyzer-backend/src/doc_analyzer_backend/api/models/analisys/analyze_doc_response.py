from agent_enums import Role
from pydantic import BaseModel

from src.doc_analyzer_backend.api.models.analisys.result_data import ResultData
from src.doc_analyzer_backend.llm.tokens.token_usage import TokenUsage


class AnalyzeDocResponse(BaseModel):
    result: list[ResultData]
    role: Role
    token_usage: TokenUsage | None
    total_token_usage: TokenUsage | None
    elapsed: float
    cost_rub: float
