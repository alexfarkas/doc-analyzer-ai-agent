from pydantic import BaseModel


class CouncilAnalyzeDocResponse(BaseModel):
    result: str
    elapsed: float
