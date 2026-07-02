from agent_enums import Assignment
from pydantic import BaseModel


class AgentData(BaseModel):
    model: str | None = None
    assignment: Assignment
