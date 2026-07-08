from pydantic import BaseModel


class CreateCouncilResponse(BaseModel):
    result: str
