from pydantic import BaseModel

from api.config.limit_data import LimitSettings
from api.models.config.role_data import RoleData


class ConfigResponse(BaseModel):
    limit_settings: LimitSettings
    roles: list[RoleData]
