import uuid
from datetime import datetime, timezone

from src.doc_analyzer_backend.session.data.user_session import UserSession


class UserManager:
    def __init__(self):
        self._user_sessions: dict[str, UserSession] = {}

    def create_session(self) -> UserSession:
        session_id = str(uuid.uuid4())
        session = UserSession(session_id=session_id)
        self._user_sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> UserSession | None:
        return self._user_sessions.get(session_id)

    def get_or_create_session(self, session_id: str) -> UserSession:
        session = self._user_sessions.get(session_id)
        if session:
            return session
        return self._create_session_with_id(session_id)

    def delete_session(self, session_id: str) -> bool:
        if session_id in self._user_sessions:
            del self._user_sessions[session_id]
            return True
        return False

    def cleanup_inactive(self, max_age_seconds: int = 3600) -> int:
        now = datetime.now(timezone.utc)
        to_delete = []
        for session_id, session in self._user_sessions.items():
            age = (now - session.last_active_at).total_seconds()
            if age > max_age_seconds:
                to_delete.append(session_id)
        for session_id in to_delete:
            del self._user_sessions[session_id]
        return len(to_delete)

    def _create_session_with_id(self, session_id: str) -> UserSession:
        session = UserSession(session_id=session_id)
        self._user_sessions[session_id] = session
        return session


user_manager = UserManager()
