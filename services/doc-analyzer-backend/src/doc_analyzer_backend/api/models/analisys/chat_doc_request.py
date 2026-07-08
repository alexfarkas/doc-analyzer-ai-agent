from pydantic import BaseModel

from src.doc_analyzer_backend.api.models.analisys.agent_data import AgentData


class ChatDocRequest(BaseModel):
    user_message: str
    agent_index: int
    agents: list[AgentData]
    model: str
