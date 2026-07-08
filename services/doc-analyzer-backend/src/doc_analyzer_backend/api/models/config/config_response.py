from pydantic import BaseModel

from src.doc_analyzer_backend.api.config.limit_data import LimitSettings
from src.doc_analyzer_backend.api.models.config.role_data import RoleData


class ConfigResponse(BaseModel):
    limit_settings: LimitSettings
    roles: list[RoleData]
