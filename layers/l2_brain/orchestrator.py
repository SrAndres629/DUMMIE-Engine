import logging
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger("brain.orchestrator")


class _LessonsUseCaseBridge:
    def __init__(self, ledger_audit: Any):
        self._ledger_audit = ledger_audit

    def _json_safe(self, value: Any):
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, dict):
            return {k: self._json_safe(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [self._json_safe(v) for v in value]
        if hasattr(value, "__dict__"):
            return self._json_safe(value.__dict__)
        return value

    def execute_error(self, context: Any, error: Exception, tick: int, correction: str):
        entry = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "issue": str(error),
            "correction": correction,
            "tick": tick,
            "context": self._json_safe(getattr(context, "__dict__", str(context))),
        }
        if hasattr(self._ledger_audit, "log_lesson"):
            self._ledger_audit.log_lesson(entry)

    def execute_ambiguity(self, context: Any, ambiguity: str, plan: str):
        entry = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "ambiguity": ambiguity,
            "plan": plan,
            "context": self._json_safe(getattr(context, "__dict__", str(context))),
        }
        if hasattr(self._ledger_audit, "log_ambiguity"):
            self._ledger_audit.log_ambiguity(entry)


class CognitiveOrchestrator:
    """
    [L2_BRAIN] Orquestador Cognitivo (Legacy/Bridge).
    Actúa como fachada para el nuevo Antigravity Daemon.
    """
    def __init__(self, shield_port: Any, event_store: Any, ledger_audit: Any, session_ledger: Any, skill_repo: Any):
        self.shield = shield_port
        self.event_store = event_store
        self.ledger_audit = ledger_audit
        self.session_ledger = session_ledger
        self.skill_repo = skill_repo
        # Bridge compatibility: L1 MCP tools read this clock directly.
        self.lamport_clock = 0
        self.lessons_use_case = _LessonsUseCaseBridge(ledger_audit)
        logger.info("CognitiveOrchestrator Materialized (Tabula Rasa Bridge)")

    async def process_intent(self, intent: Any):
        self.lamport_clock += 1
        logger.info(f"Processing intent: {getattr(intent, 'goal', str(intent))}")
        return {"status": "ACK", "intent_id": "LEGACY-01"}

    async def handle_task(self, intent: Any):
        # Legacy MCP tools call handle_task and expect this status string.
        await self.process_intent(intent)
        return "INTENT_QUEUED_L2_VALIDATED"
