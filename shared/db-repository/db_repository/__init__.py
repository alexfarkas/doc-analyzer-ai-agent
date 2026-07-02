"""
db-repository - клиент к базе данных для хранения и работы с данными ИИ-агента

Содержит:
- PromptModel
- PromptDB
- PromptRepository
"""

from db_repository.prompt_model import PromptModel
from db_repository.repository import PromptRepository, PromptDB

__version__ = "1.0.0"

__all__ = [
    "PromptModel",
    "PromptDB",
    "PromptRepository",
]
