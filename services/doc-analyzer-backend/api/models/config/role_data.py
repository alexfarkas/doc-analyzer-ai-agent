from pydantic import BaseModel

from api.models.config.assignment_data import AssignmentData
from api.models.config.model_data import ModelData


class RoleData(BaseModel):
    api_param: str
    ui_title: str
    models: list[ModelData]
    assignments: list[AssignmentData]
    max_agents: int
