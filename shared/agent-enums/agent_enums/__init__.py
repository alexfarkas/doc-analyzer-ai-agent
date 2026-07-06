"""
agent-enums - общие enum для сервисов ИИ-агента

Содержит enum:
- Mode
- Role
- Assignment
- PromptType
"""

from agent_enums.answer_status import AnswerStatus
from agent_enums.assignment import Assignment
from agent_enums.modes import Mode
from agent_enums.prompt_type import PromptType
from agent_enums.role import Role

__version__ = "1.0.0"

__all__ = [
    "AnswerStatus",
    "Assignment",
    "Mode",
    "PromptType",
    "Role",
]
