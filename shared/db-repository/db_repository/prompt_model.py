from agent_enums import Mode, Role, PromptType, Assignment
from pydantic import BaseModel, field_validator


class PromptModel(BaseModel):
    mode: Mode
    role: Role
    assignment: Assignment
    prompt_type: PromptType
    content: str

    @field_validator("mode", "role", "assignment", "prompt_type", mode="before")
    @classmethod
    def _convert_to_enum(cls, v, info):
        if isinstance(v, str):
            field_name = info.field_name
            enum_cls = {
                "mode": Mode,
                "role": Role,
                "assignment": Assignment,
                "prompt_type": PromptType,
            }[field_name]
            return enum_cls(v)
        return v
