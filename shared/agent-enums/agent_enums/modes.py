from enum import Enum


class Mode(str, Enum):
    ANALYSIS = "analysis"
    CLARIFICATION = "clarification"
    CHAT = "chat"
