from datetime import datetime, timezone
from dummie.paths import ROOT
from layers.l2_brain.session_store import SessionStore

class DummieSessionManager:
    def __init__(self):
        self.store = SessionStore(ROOT)
        self._ensure_current_session()

    def _ensure_current_session(self):
        try:
            self.store.load_session("CURRENT")
        except FileNotFoundError:
            self.store.create_session("CURRENT", {"description": "Auto-generated daily cockpit session"})

    def record_episode(self, query: str, intent: str, answer: str, decision: str = "PASS", evidence_refs: list[str] = None):
        episode = {
            "query": query,
            "intent": intent,
            "answer": answer,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evidence_refs": evidence_refs or [],
            "decision": decision
        }
        try:
            self.store.append_learning_episode("CURRENT", episode)
        except Exception:
            pass
