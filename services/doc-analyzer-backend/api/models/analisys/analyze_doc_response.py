from pydantic import BaseModel

from api.models.analisys.result_data import ResultData
from llm.token_usage import TokenUsage


class AnalyzeDocResponse(BaseModel):
    result: list[ResultData]
    token_usage: TokenUsage
    total_token_usage: TokenUsage
    elapsed: float
    cost_rub: float
