from pydantic import BaseModel


class AssignmentData(BaseModel):
    api_param: str
    ui_title: str
