from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from dummie.paths import ROOT

try:
    from layers.l2_brain.session_store import SessionStore, SessionRole
except ModuleNotFoundError:
    from layers.l2_brain.memory.session_store import SessionStore, SessionRole


class DummieSessionManager:
    def __init__(self):
        self.store = SessionStore(ROOT)
        self.session_id = "CURRENT"
        self._ensure_current_session()

    def _ensure_current_session(self) -> None:
        try:
            self.store.load_session(self.session_id)
        except FileNotFoundError:
            self.store.create_session(
                self.session_id,
                {
                    "description": "DUMMIE sovereign runtime session",
                    "role": SessionRole.GENERAL.value,
                },
            )

    def get_or_create_role_session(
        self, role: SessionRole, context_id: str = ""
    ) -> dict:
        return self.store.find_or_create_session(role=role, context_id=context_id)

    def get_session(self, session_id: Optional[str] = None) -> dict:
        sid = session_id or self.session_id
        return self.store.load_session(sid)

    def record_episode(
        self,
        query: str,
        intent: str,
        answer: str,
        decision: str = "PASS",
        evidence_refs: list[str] | None = None,
        session_id: str = "",
    ) -> bool:
        sid = session_id or self.session_id
        episode = {
            "query": query,
            "intent": intent,
            "answer": answer,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evidence_refs": evidence_refs or [],
            "decision": decision,
        }
        self.store.append_learning_episode(sid, episode)
        return True

    def close_session(self, session_id: str = "") -> dict:
        return self.store.close_session(session_id or self.session_id)

    def list_role_sessions(self, role: SessionRole) -> list:
        return self.store.list_sessions_by_role(role)

    def list_active(self) -> list:
        return self.store.list_active_sessions()
