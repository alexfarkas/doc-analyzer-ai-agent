from enum import Enum


class PromptType(str, Enum):
    SYSTEM = "system"
    USER = "user"
