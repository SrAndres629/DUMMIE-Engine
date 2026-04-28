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
        goal = getattr(intent, "goal", "") or getattr(intent, "rationale", str(intent))
        logger.info(f"Processing intent: {goal}")
        
        # Persistencia 4D-TES (Spec 02)
        if self.event_store and self.event_store.conn:
            import hashlib
            import time
            from enum import Enum
            
            parent_hash = self.event_store.get_last_leaf_hash()
            
            # Generar hash causal (Merkle-DAG simplificado)
            content = f"{parent_hash}|{self.lamport_clock}|{goal}"
            causal_hash = hashlib.sha256(content.encode()).hexdigest()[:24]
            
            now_ms = int(time.time() * 1000)
            
            # Extraer dimensiones (Spec 12 / 6D Model)
            locus_x = getattr(intent, "locus_x", "sw.strategy.discovery")
            authority_a = getattr(intent, "authority_a", "HUMAN")
            if isinstance(authority_a, Enum): authority_a = authority_a.value
            intent_i = getattr(intent, "intent_i", "RESOLUTION")
            if isinstance(intent_i, Enum): intent_i = intent_i.value
            
            safe_summary = goal.replace("'", "''")
            
            cypher = (
                f"CREATE (m:MemoryNode4D {{"
                f"causal_hash: '{causal_hash}', "
                f"parent_hash: '{parent_hash}', "
                f"lamport_t: {self.lamport_clock}, "
                f"locus_x: '{locus_x}', "
                f"locus_y: 'L1_TRANSPORT', "
                f"locus_z: 'L2_BRAIN', "
                f"authority_a: '{authority_a}', "
                f"intent_i: '{intent_i}', "
                f"summary: '{safe_summary}', "
                f"timestamp: {now_ms}}})"
            )
            
            try:
                self.event_store.query(cypher)
                logger.info(f"4D-TES Persistence OK: {causal_hash}")
                return {"status": "ACK", "intent_id": causal_hash}
            except Exception as e:
                logger.error(f"4D-TES Persistence Failed: {e}")
                # Fallback para no romper el flujo principal
        
        return {"status": "ACK", "intent_id": "LEGACY-01"}

    async def handle_task(self, intent: Any):
        # Legacy MCP tools call handle_task and expect this status string.
        result = await self.process_intent(intent)
        if result.get("intent_id") != "LEGACY-01":
            return f"INTENT_QUEUED_L2_VALIDATED:{result['intent_id']}"
        return "INTENT_QUEUED_L2_VALIDATED"
