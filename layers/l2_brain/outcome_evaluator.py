import logging
from typing import Any, Dict, List, Optional
from layers.l2_brain.gateway_contract import SagaTransaction
from dataclasses import dataclass

logger = logging.getLogger("dummie.brain.outcome")

@dataclass
class CapabilityAmplificationResult:
    score: float
    verdict: str
    next: str

class OutcomeEvaluator:
    """
    [L2_BRAIN] Evaluador de Resultados de Sagas.
    Encapsula la lógica para construir el reporte final de una transacción cognitiva.
    """
    def __init__(self, daemon: Any = None):
        self.daemon = daemon

    def calculate_capability_amplification(self, current_metrics: dict, baseline_metrics: Optional[dict] = None) -> CapabilityAmplificationResult:
        if not baseline_metrics:
            return CapabilityAmplificationResult(score=0.0, verdict="insufficient_baseline", next="collect_more_metrics")
        
        score = 0.0
        
        if current_metrics.get("tests_passed") and not baseline_metrics.get("tests_passed"):
            score += 10.0
        elif not current_metrics.get("tests_passed") and baseline_metrics.get("tests_passed"):
            score -= 10.0
            
        score += baseline_metrics.get("human_interventions", 0) - current_metrics.get("human_interventions", 0)
        score += baseline_metrics.get("regressions", 0) - current_metrics.get("regressions", 0)
        score += current_metrics.get("memory_reuse_gain", 0.0)
        score += current_metrics.get("mentor_quality_gain", 0.0)
        
        token_diff = baseline_metrics.get("input_tokens", 0) + baseline_metrics.get("output_tokens", 0) - \
                     (current_metrics.get("input_tokens", 0) + current_metrics.get("output_tokens", 0))
        score += token_diff / 1000.0
        
        if score > 0:
            return CapabilityAmplificationResult(score=score, verdict="improved", next="continue_collecting_metrics")
        else:
            return CapabilityAmplificationResult(score=score, verdict="regressed", next="inspect_regression_causes")

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
            "metacognition_status": self.daemon.metacognition_status if self.daemon else "UNKNOWN",
            "gate_status": gate_status,
            "gate_reasons": gate_reasons or ["all_guards_passed"],
            "gateway_first_policy": f"{self.daemon.gateway_policy.mode.value}_MODE_ACTIVE" if self.daemon and hasattr(self.daemon, "gateway_policy") else "UNKNOWN",
            "cognitive_preflight": self.daemon.last_cognitive_preflight if self.daemon else {},
            "steps": [{"task_id": step.task_id, "status": step.status} for step in saga.steps],
        }

        # Efficiency Stats from Runtime Meter
        if self.daemon and hasattr(self.daemon, "runtime_meter") and self.daemon.runtime_meter:
            outcome["efficiency"] = self.daemon.runtime_meter.get_stats()
            
        # Token Economy Summary from Ledger
        if self.daemon and hasattr(self.daemon, "token_ledger") and self.daemon.token_ledger:
            outcome["token_economy"] = self.daemon.token_ledger.summarize_session(saga.transaction_id)
            if "cost_estimate" not in outcome["token_economy"]:
                outcome["token_economy"]["cost_estimate"] = self.daemon.token_ledger.cloud_cost_estimate(saga.transaction_id)

        # Integración de Metadatos de Metacognición si están disponibles
        if self.daemon and hasattr(self.daemon, "metacognition") and self.daemon.metacognition:
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
