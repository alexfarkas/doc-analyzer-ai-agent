from pydantic import BaseModel


class StatusResponse(BaseModel):
    model: str
    temperature: float
    tools: list[ToolData]
    use_rag: bool
    rag: RAGData | None


class ToolData(BaseModel):
    name: str
    description: str


class RAGData(BaseModel):
    model: str
    top_k: int
    similarity_threshold: float
