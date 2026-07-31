from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.doc_analyzer_backend.session.data.user_data import UserData


@dataclass
class UserSession:
    session_id: str

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    data: UserData = field(default_factory=UserData)
