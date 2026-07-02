from agent_enums import Role
from pydantic import BaseModel

from api.models.analisys.agent_data import AgentData


class AnalyzeDocRequest(BaseModel):
    resources: list[str]
    role: Role
    agents: list[AgentData]
    encoding: str = "utf-8"
