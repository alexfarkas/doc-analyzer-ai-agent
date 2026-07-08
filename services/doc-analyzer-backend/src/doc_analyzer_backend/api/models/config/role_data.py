from pydantic import BaseModel

from src.doc_analyzer_backend.api.models.config.assignment_data import AssignmentData
from src.doc_analyzer_backend.api.models.config.model_data import ModelData


class RoleData(BaseModel):
    api_param: str
    ui_title: str
    models: list[ModelData]
    assignments: list[AssignmentData]
    max_agents: int
