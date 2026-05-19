from __future__ import annotations

from datetime import datetime, timezone

from dummie.paths import ROOT
from layers.l2_brain.session_store import SessionStore


class DummieSessionManager:
    def __init__(self):
        self.store = SessionStore(ROOT)
        self.session_id = "CURRENT"
        self._ensure_current_session()

    def _ensure_current_session(self) -> None:
        try:
            self.store.load_session(self.session_id)
        except FileNotFoundError:
            self.store.create_session(self.session_id, {"description": "DUMMIE sovereign runtime session"})

    def record_episode(
        self,
        query: str,
        intent: str,
        answer: str,
        decision: str = "PASS",
        evidence_refs: list[str] | None = None,
    ) -> bool:
        episode = {
            "query": query,
            "intent": intent,
            "answer": answer,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evidence_refs": evidence_refs or [],
            "decision": decision,
        }
        self.store.append_learning_episode(self.session_id, episode)
        return True
