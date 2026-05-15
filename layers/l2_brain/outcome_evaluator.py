import logging
from typing import Any, Dict, List, Optional
from layers.l2_brain.gateway_contract import SagaTransaction
from dataclasses import dataclass
from enum import Enum

from layers.l2_brain.daemon_outcome import (
    DaemonOutcome,
    EfficiencyMetrics,
    MetacognitionStatus,
    ModelRouteMetadata,
    NextAction,
    RecoveryHint,
    SensorFirstStatus,
    TestExecutionSummary,
)

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
        session_id: str = "",
        mission_id: str = "",
        phase_id: str = "",
        authority_level: str = "",
        intent_type: str = "",
        model_route: Optional[Dict[str, Any]] = None,
        tests: Optional[Dict[str, Any]] = None,
        evidence_refs: Optional[List[str]] = None,
        next_action: Optional[Dict[str, Any]] = None,
        learning_episode_ref: str = "",
    ) -> Dict[str, Any]:
        """
        Construye el DTO final de resultado de la saga.
        """
        gate_reasons = gate_reasons or ["all_guards_passed"]
        daemon_outcome = self.build_daemon_outcome(
            status=status,
            transaction_id=transaction_id,
            saga=saga,
            gate_status=gate_status,
            gate_reasons=gate_reasons,
            session_id=session_id,
            mission_id=mission_id,
            phase_id=phase_id,
            authority_level=authority_level,
            intent_type=intent_type,
            model_route=model_route,
            tests=tests,
            evidence_refs=evidence_refs,
            next_action=next_action,
            learning_episode_ref=learning_episode_ref,
        )
        outcome = daemon_outcome.to_dict()
        outcome["error"] = error
        outcome["metacognition_status"] = daemon_outcome.metacognition.status if self.daemon else "UNKNOWN"
        outcome["gate_status"] = gate_status
        outcome["gate_reasons"] = gate_reasons
        outcome["gateway_first_policy"] = f"{daemon_outcome.sensor_first.mode}_MODE_ACTIVE" if self.daemon else "UNKNOWN"
        outcome["cognitive_preflight"] = _safe_getattr(self.daemon, "last_cognitive_preflight", {}) if self.daemon else {}
        outcome["steps"] = [{"task_id": step.task_id, "status": step.status} for step in saga.steps]

        # Token Economy Summary from Ledger
        if self.daemon and hasattr(self.daemon, "token_ledger") and self.daemon.token_ledger:
            outcome["token_economy"] = self.daemon.token_ledger.summarize_session(saga.transaction_id)
            if "cost_estimate" not in outcome["token_economy"]:
                outcome["token_economy"]["cost_estimate"] = self.daemon.token_ledger.cloud_cost_estimate(saga.transaction_id)

        # Integración de Metadatos de Metacognición si están disponibles
        if self.daemon and hasattr(self.daemon, "metacognition") and self.daemon.metacognition:
            # Notamos que el frame se pasa externamente o se recupera del daemon
            pass 

        mission_state = _mission_state_from(self.daemon, outcome.get("mission_id", ""))
        if mission_state:
            outcome["current_mission_state"] = mission_state
            if not next_action and mission_state.get("next_action"):
                outcome["next_action"] = mission_state["next_action"]

        return outcome

    def build_daemon_outcome(
        self,
        status: str,
        transaction_id: str,
        saga: SagaTransaction,
        gate_status: str = "ALLOW",
        gate_reasons: Optional[List[str]] = None,
        session_id: str = "",
        mission_id: str = "",
        phase_id: str = "",
        authority_level: str = "",
        intent_type: str = "",
        model_route: Optional[Dict[str, Any]] = None,
        tests: Optional[Dict[str, Any]] = None,
        evidence_refs: Optional[List[str]] = None,
        next_action: Optional[Dict[str, Any]] = None,
        learning_episode_ref: str = "",
    ) -> DaemonOutcome:
        gate_reasons = gate_reasons or ["all_guards_passed"]
        return DaemonOutcome(
            outcome_id=f"outcome-{transaction_id}",
            status=status,
            session_id=session_id or _safe_getattr(self.daemon, "session_id", ""),
            mission_id=mission_id or _safe_getattr(self.daemon, "mission_id", ""),
            phase_id=phase_id or _safe_getattr(self.daemon, "phase_id", ""),
            transaction_id=transaction_id,
            context_token=saga.context_token,
            authority_level=_enum_value(authority_level or _safe_getattr(self.daemon, "authority_level", "")),
            intent_type=_enum_value(intent_type or _safe_getattr(self.daemon, "intent_type", "")),
            model_route=_model_route_from(self.daemon, model_route),
            metacognition=_metacognition_from(self.daemon),
            sensor_first=_sensor_first_from(self.daemon, gate_status, gate_reasons),
            efficiency=_efficiency_from(self.daemon),
            tests=_tests_from(tests),
            evidence_refs=evidence_refs or [],
            next_action=_next_action_from(next_action, status, gate_reasons),
            recovery_hint=RecoveryHint(can_resume=status in {"SUCCESS", "PARTIAL", "DEGRADED", "BLOCKED"}, resume_from=phase_id or ""),
            learning_episode_ref=learning_episode_ref,
        )

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


def _safe_getattr(source: Any, name: str, default: Any = "") -> Any:
    if source is None:
        return default
    value = getattr(source, name, default)
    if hasattr(value, "assert_called") or value.__class__.__module__.startswith("unittest.mock"):
        return default
    return value


def _enum_value(value: Any) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)


def _model_route_from(daemon: Any, explicit: Optional[Dict[str, Any]]) -> ModelRouteMetadata:
    source = explicit or _safe_getattr(daemon, "last_model_route", {}) or {}
    if not isinstance(source, dict):
        return ModelRouteMetadata()
    return ModelRouteMetadata(
        tier=_enum_value(source.get("tier", "")) if source.get("tier", "") else "",
        provider=str(source.get("provider", "")),
        reason=str(source.get("reason", "")),
        hook_metadata=dict(source.get("hook_metadata", {}) or {}),
    )


def _metacognition_from(daemon: Any) -> MetacognitionStatus:
    status = _safe_getattr(daemon, "metacognition_status", "MISSING") or "MISSING"
    if status == "ERROR":
        status = "DEGRADED"
    error = _safe_getattr(daemon, "metacognition_error", "") or ""
    pipeline = _safe_getattr(daemon, "metacognition", None)
    hooks: list[str] = []
    for attr in ("input_hooks", "deliberation_hooks", "output_hooks"):
        values = getattr(pipeline, attr, []) if pipeline else []
        if isinstance(values, list):
            hooks.extend(type(item).__name__ for item in values)
    return MetacognitionStatus(status=status, error=error, enabled_hooks=hooks)


def _sensor_first_from(daemon: Any, gate_status: str, gate_reasons: List[str]) -> SensorFirstStatus:
    mode = "WARN"
    policy = _safe_getattr(daemon, "gateway_policy", None)
    if policy is not None:
        mode_value = getattr(getattr(policy, "mode", None), "value", None)
        if mode_value:
            mode = str(mode_value)
    decision = "ALLOW" if gate_status == "ALLOW" else "BLOCK" if gate_status == "BLOCK" else "WARN"
    return SensorFirstStatus(mode=mode, decision=decision, reason="; ".join(gate_reasons))


def _efficiency_from(daemon: Any) -> EfficiencyMetrics:
    meter = getattr(daemon, "runtime_meter", None) if daemon is not None else None
    stats = meter.get_stats() if meter and hasattr(meter, "get_stats") else {}
    if not isinstance(stats, dict):
        stats = {}

    measurement_type = str(stats.get("measurement_type", "estimated"))
    if measurement_type.startswith("runtime"):
        measurement_type = "runtime"

    return EfficiencyMetrics(
        input_tokens=int(stats.get("actual_direct_tokens", stats.get("input_tokens", 0)) or 0),
        cached_tokens=int(stats.get("cached_tokens", 0) or 0),
        output_tokens=int(stats.get("actual_gateway_tokens", stats.get("output_tokens", 0)) or 0),
        estimated_direct_tokens=int(stats.get("estimated_direct_tokens", 0) or 0),
        estimated_gateway_tokens=int(stats.get("estimated_gateway_tokens", 0) or 0),
        token_reduction_ratio=float(stats.get("token_reduction_ratio", 0.0) or 0.0),
        measurement_type=measurement_type,
    )


def _tests_from(value: Optional[Dict[str, Any]]) -> TestExecutionSummary:
    value = value or {}
    return TestExecutionSummary(
        commands=list(value.get("commands", []) or []),
        passed=int(value.get("passed", 0) or 0),
        failed=int(value.get("failed", 0) or 0),
    )


def _next_action_from(value: Optional[Dict[str, Any]], status: str, gate_reasons: List[str]) -> NextAction:
    if value:
        return NextAction(
            recommended=str(value.get("recommended", "")),
            reason=str(value.get("reason", "")),
            blocked_by=list(value.get("blocked_by", []) or []),
        )
    if status == "SUCCESS":
        return NextAction(recommended="continue", reason="outcome_success")
    return NextAction(recommended="inspect", reason="outcome_not_success", blocked_by=list(gate_reasons))


def _mission_state_from(daemon: Any, mission_id: str) -> dict:
    if not daemon or not mission_id:
        return {}
    mission_runtime = _safe_getattr(daemon, "mission_runtime", None)
    if not mission_runtime or not hasattr(mission_runtime, "current_state"):
        return {}
    try:
        state = mission_runtime.current_state(mission_id)
    except Exception as exc:
        return {
            "mission_id": mission_id,
            "status": "unavailable",
            "error": str(exc),
        }
    return state if isinstance(state, dict) else {}
