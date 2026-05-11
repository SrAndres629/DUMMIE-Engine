import logging
from typing import Any, Dict, List, Optional
from layers.l2_brain.gateway_contract import SagaTransaction

logger = logging.getLogger("dummie.brain.outcome")

class OutcomeEvaluator:
    """
    [L2_BRAIN] Evaluador de Resultados de Sagas.
    Encapsula la lógica para construir el reporte final de una transacción cognitiva.
    """
    def __init__(self, daemon: Any):
        self.daemon = daemon

    def build_outcome(
        self,
        status: str,
        transaction_id: str,
        saga: SagaTransaction,
        error: str = "",
        gate_status: str = "ALLOW",
        gate_reasons: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Construye el DTO final de resultado de la saga.
        """
        outcome = {
            "status": status,
            "transaction_id": transaction_id,
            "error": error,
            "metacognition_status": self.daemon.metacognition_status,
            "gate_status": gate_status,
            "gate_reasons": gate_reasons or ["all_guards_passed"],
            "gateway_first_policy": f"{self.daemon.gateway_policy.mode.value}_MODE_ACTIVE",
            "cognitive_preflight": self.daemon.last_cognitive_preflight,
            "steps": [{"task_id": step.task_id, "status": step.status} for step in saga.steps],
        }

        # Efficiency Stats from Runtime Meter
        if hasattr(self.daemon, "runtime_meter") and self.daemon.runtime_meter:
            outcome["efficiency"] = self.daemon.runtime_meter.get_stats()

        # Integración de Metadatos de Metacognición si están disponibles
        if hasattr(self.daemon, "metacognition") and self.daemon.metacognition:
            # Notamos que el frame se pasa externamente o se recupera del daemon
            pass 

        return outcome

    def enrich_with_metacognition(self, outcome: Dict[str, Any], frame: Any) -> Dict[str, Any]:
        """
        Enriquece el resultado con hallazgos del pipeline metacognitivo.
        """
        if frame:
            outcome["metacognition"] = {
                "authority": frame.authority_level.value if hasattr(frame.authority_level, "value") else str(frame.authority_level),
                "mission_steps": len(getattr(frame, "mission_plan", [])),
                "verification": getattr(frame, "verification_findings", []),
                "required_tools": getattr(frame, "required_tools", []),
                "risk_level": getattr(frame, "risk_level", "unknown"),
            }
        return outcome
