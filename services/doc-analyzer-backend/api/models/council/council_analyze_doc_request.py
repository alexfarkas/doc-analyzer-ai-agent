from agent_enums import Role
from pydantic import BaseModel


class CouncilAnalyzeDocRequest(BaseModel):
    resources: list[str]
    role: Role
