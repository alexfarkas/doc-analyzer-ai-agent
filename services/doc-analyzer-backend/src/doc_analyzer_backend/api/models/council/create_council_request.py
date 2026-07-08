from pydantic import BaseModel


class CreateCouncilRequest(BaseModel):
    size: int
