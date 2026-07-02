from pydantic import BaseModel

from api.models.analisys.agent_data import AgentData


class ClarifyDocRequest(BaseModel):
    ai_answer: str
    user_message: str
    agent_index: int
    agents: list[AgentData]
    model: str
