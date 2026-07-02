from pydantic import BaseModel

from api.models.config.role_data import RoleData


class ConfigResponse(BaseModel):
    roles: list[RoleData]
