# Spec: 164_heartbeat_lifecycle_runtime
# Spec: DE-V2-L2-164
"""Heartbeat Lifecycle Runtime — HEARTBEAT-0

Orchestrates a full observe → reason → queue → learn cycle.
Mode: observe_only | advisory | repair_planning
Never executes mutations autonomously.
"""

# Spec Reference: 190_full_body_operational_auditor
import json
import uuid
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Data contracts
# ---------------------------------------------------------------------------

@dataclass
class HeartbeatObservation:
    git_clean: bool
    canonical_inputs: List[str]
    missing_inputs: List[str]
    active_blockers: List[str]
    kuzu_degraded: bool
    readiness_score: float
    quarantined_models: int
    test_debt_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HeartbeatOutcome:
    heartbeat_id: str
    mode: str
    decision: str
    observation: Dict[str, Any]
    truth_hygiene: Dict[str, Any]
    epistemic_state: Dict[str, Any]
    bias_report: Dict[str, Any]
    memory_spine: Dict[str, Any]
    mental_model: Dict[str, Any]
    dialectic: Dict[str, Any]
    quality_gate: Dict[str, Any]
    self_improvement_queue: Dict[str, Any]
    selected_action: Dict[str, Any]
    blocked_actions: List[str]
    dispatch_recommendation: str
    outcome_ref: str
    learning_episode_ref: str
    next_heartbeat_seed: Dict[str, Any]
    warnings: List[str]
    evidence_refs: List[str]
    created_at: str
    circulation_summary: Dict[str, Any] = field(default_factory=dict)
    dependency_reality: Dict[str, Any] = field(default_factory=dict)
    degraded_capabilities: Dict[str, Any] = field(default_factory=dict)
    toolchain_probe: Dict[str, Any] = field(default_factory=dict)
    runtime_closure_plan: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load(path: Path) -> Dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _is_kuzu_degraded(aiwg_root: Path) -> bool:
    reports = aiwg_root / "reports"
    governor = _load(reports / "capability_promotion_governor_latest.json")
    for cap in governor.get("capabilities", []):
        if cap.get("capability_id") == "kuzu_4dtes_persistence":
            return cap.get("verified_status") in ("DEGRADED", "SIMULATED", "MISSING")
    
    # fallback to old logic
    readiness = _load(reports / "readiness_score_calibration_latest.json")
    for f in readiness.get("findings", []):
        if "degraded" in f.get("id", "").lower() or "degraded" in f.get("description", "").lower():
            return True
    return True  # conservative default


# ---------------------------------------------------------------------------
# Core heartbeat
# ---------------------------------------------------------------------------

def run_heartbeat(mode: str = "observe_only", aiwg_root: Path = Path(".aiwg")) -> Dict[str, Any]:
    """Execute one full heartbeat cycle."""
    l2 = Path("layers/l2_brain").resolve()
    if str(l2) not in sys.path:
        sys.path.insert(0, str(l2))

    reports = aiwg_root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    hb_id = f"hb-{uuid.uuid4().hex[:8]}"
    warnings: List[str] = []
    evidence: List[str] = []

    # ---- STEP 0: WHOLE-BODY OPERATIONAL VERIFICATION AUDITS ----
    try:
        from dependency_reproducibility_verifier import run_dependency_reproducibility_verification
        from kuzu_graph_readback_verifier import run_kuzu_graph_readback_verification
        from embedding_activation_verifier import run_embedding_activation_verification
        from capability_promotion_governor import run_capability_promotion_governor
        from full_body_operational_auditor import run_full_body_operational_audit
        from whole_body_repair_queue import run_whole_body_repair_queue

        run_dependency_reproducibility_verification()
        run_kuzu_graph_readback_verification()
        run_embedding_activation_verification()
        run_capability_promotion_governor()
        run_full_body_operational_audit()
        run_whole_body_repair_queue()
        
        evidence.extend([
            ".aiwg/reports/dependency_reproducibility_latest.json",
            ".aiwg/reports/kuzu_graph_readback_verification_latest.json",
            ".aiwg/reports/embedding_activation_verification_latest.json",
            ".aiwg/reports/capability_promotion_governor_latest.json",
            ".aiwg/reports/full_body_operational_audit_latest.json",
            ".aiwg/reports/whole_body_repair_queue_latest.json"
        ])
    except Exception as e:
        warnings.append(f"whole_body_verification_audits_failed: {e}")

    # ---- STEP 1: OBSERVE ----
    canonical = [
        "self_improvement_action_queue.json",
        "mental_model_truth_hygiene_latest.json",
        "evolution_delta_application_latest.json",
        "readiness_score_calibration_latest.json",
        "memory_spine_entrypoint_latest.json",
        "epistemic_state_latest.json",
        "metacognitive_loop_latest.json",
        "cognitive_bias_report_latest.json",
        "whole_body_scan_latest.json",
        "whole_body_scan_calibration_latest.json",
        "wiring_matrix_latest.json",
        "shadow_runtime_classification_latest.json",
        "dependency_reproducibility_latest.json",
        "kuzu_graph_readback_verification_latest.json",
        "embedding_activation_verification_latest.json",
        "capability_promotion_governor_latest.json",
        "full_body_operational_audit_latest.json",
        "whole_body_repair_queue_latest.json"
    ]
    found = [c for c in canonical if (reports / c).exists()]
    missing = [c for c in canonical if c not in found]
    kuzu_degraded = _is_kuzu_degraded(aiwg_root)

    hygiene_data = _load(reports / "mental_model_truth_hygiene_latest.json")
    quarantined_count = hygiene_data.get("summary", {}).get("quarantined_count", 0)

    readiness_data = _load(reports / "readiness_score_calibration_latest.json")
    readiness_score = readiness_data.get("calibrated_scores", {}).get("overall", 0)

    calibration = _load(reports / "whole_body_scan_calibration_latest.json")
    wiring = _load(reports / "wiring_matrix_latest.json")
    shadow = _load(reports / "shadow_runtime_classification_latest.json")
    scan_latest = _load(reports / "whole_body_scan_latest.json")

    coherence_score = scan_latest.get("overall_coherence_score", 0.0)

    # Count test debt
    test_triage = _load(reports / "test_debt_triage_latest.json")
    test_debt = test_triage.get("missing_tests_count", 0) + test_triage.get("failing_tests_count", 0)

    active_blockers = []
    if kuzu_degraded:
        active_blockers.append("kuzu_degraded")
    if quarantined_count > 0:
        active_blockers.append(f"quarantined_models_{quarantined_count}")
    if calibration.get("decision") == "FAIL":
        active_blockers.append("scanner_calibration_failed")
    if wiring.get("decision") == "FAIL":
        active_blockers.append("wiring_matrix_failed")
    if shadow.get("decision") == "FAIL":
        active_blockers.append("shadow_classification_failed")

    observation = HeartbeatObservation(
        git_clean=True,
        canonical_inputs=found,
        missing_inputs=missing,
        active_blockers=active_blockers,
        kuzu_degraded=kuzu_degraded,
        readiness_score=readiness_score,
        quarantined_models=quarantined_count,
        test_debt_count=test_debt,
    )
    
    observation_dict = observation.to_dict()
    observation_dict["whole_body_scan"] = {
        "overall_coherence_score": coherence_score,
        "calibration_decision": calibration.get("decision", "unknown"),
        "wiring_matrix_decision": wiring.get("decision", "unknown"),
        "shadow_classification_decision": shadow.get("decision", "unknown"),
        "active_modules": calibration.get("scan_metrics", {}).get("active_modules", 0),
        "shadow_modules": calibration.get("scan_metrics", {}).get("shadow_modules", 0),
        "orphaned_tests": calibration.get("scan_metrics", {}).get("orphaned_tests", 0),
        "stale_reports": calibration.get("scan_metrics", {}).get("stale_reports", 0),
        "unvalidated_specs": calibration.get("scan_metrics", {}).get("unvalidated_specs", 0),
    }

    if missing:
        warnings.append(f"Missing canonical inputs: {', '.join(missing)}")

    # ---- STEP 1.1: COGNITIVE CIRCULATION ORCHESTRATION ----
    circulation_summary = {}
    try:
        from context_circulation_runtime import run_cognitive_circulation
        circulation_summary = run_cognitive_circulation("heartbeat loop observation", aiwg_root=aiwg_root.parent)
        evidence.extend([
            ".aiwg/reports/6d_context_packet_latest.json",
            ".aiwg/reports/context_packet_optimization_latest.json",
            ".aiwg/reports/embedding_memory_router_latest.json",
            ".aiwg/reports/4dtes_persistence_preflight_latest.json",
            ".aiwg/reports/daemon_gateway_heartbeat_bridge_latest.json",
            ".aiwg/reports/polyglot_probe_latest.json"
        ])
    except Exception as e:
        warnings.append(f"context_circulation_degraded: {e}")

    # ---- STEP 1.2: ENVIRONMENT DEP AND CAPABILITY AUDIT ----
    dependency_reality = {}
    degraded_capabilities = {}
    toolchain_probe = {}
    runtime_closure_plan = {}
    try:
        from runtime_dependency_auditor import run_runtime_dependency_audit
        from degraded_capability_registry import run_degraded_capability_registry
        from environment_toolchain_probe import run_environment_toolchain_probe
        from runtime_closure_planner import run_runtime_closure_plan

        dependency_reality = run_runtime_dependency_audit(aiwg_root=aiwg_root.parent)
        degraded_capabilities = run_degraded_capability_registry(aiwg_root=aiwg_root.parent)
        toolchain_probe = run_environment_toolchain_probe(aiwg_root=aiwg_root.parent)
        runtime_closure_plan = run_runtime_closure_plan(aiwg_root=aiwg_root.parent)

        evidence.extend([
            ".aiwg/reports/runtime_dependency_audit_latest.json",
            ".aiwg/reports/degraded_capability_registry_latest.json",
            ".aiwg/reports/environment_toolchain_probe_latest.json",
            ".aiwg/reports/runtime_closure_plan_latest.json"
        ])
    except Exception as e:
        warnings.append(f"dependency_reality_audit_failed: {e}")

    # ---- STEP 2: TRUTH HYGIENE ----
    try:
        from mental_model_truth_hygiene import run_mental_model_truth_hygiene
        truth_hygiene = run_mental_model_truth_hygiene(aiwg_root=aiwg_root)
        evidence.append(".aiwg/reports/mental_model_truth_hygiene_latest.json")
    except Exception as e:
        truth_hygiene = {"decision": "DEGRADED", "error": str(e)}
        warnings.append(f"truth_hygiene_degraded: {e}")

    # ---- STEP 3: EPISTEMIC STATE ----
    try:
        from epistemic_state_runtime import build_epistemic_state
        ep = build_epistemic_state("heartbeat observation", aiwg_root=aiwg_root)
        epistemic = ep.to_dict()
        (reports / "epistemic_state_latest.json").write_text(json.dumps(epistemic, indent=2), encoding="utf-8")
        evidence.append(".aiwg/reports/epistemic_state_latest.json")
    except Exception as e:
        epistemic = _load(reports / "epistemic_state_latest.json") or {"decision": "DEGRADED", "error": str(e)}
        warnings.append(f"epistemic_degraded: {e}")

    # ---- STEP 4: BIAS SCAN ----
    try:
        from cognitive_bias_detector import detect_cognitive_biases
        b = detect_cognitive_biases("heartbeat cycle", aiwg_root=aiwg_root)
        bias = b.to_dict() if hasattr(b, "to_dict") else b
        (reports / "cognitive_bias_report_latest.json").write_text(json.dumps(bias, indent=2), encoding="utf-8")
        evidence.append(".aiwg/reports/cognitive_bias_report_latest.json")
    except Exception as e:
        bias = _load(reports / "cognitive_bias_report_latest.json") or {"decision": "DEGRADED"}
        warnings.append(f"bias_degraded: {e}")

    # ---- STEP 5: MEMORY SPINE ----
    try:
        from memory_spine_entrypoint import retrieve_memory_for_intent
        mem = retrieve_memory_for_intent("heartbeat", aiwg_root=aiwg_root)
        memory_spine = mem.to_dict()
        evidence.append(".aiwg/reports/memory_spine_entrypoint_latest.json")
    except Exception as e:
        memory_spine = _load(reports / "memory_spine_entrypoint_latest.json") or {"status": "DEGRADED"}
        warnings.append(f"memory_spine_degraded: {e}")

    # ---- STEP 6: MENTAL MODEL LOOP (includes dialectic, quality gate) ----
    try:
        from metacognitive_loop_runtime import run_metacognitive_loop
        loop = run_metacognitive_loop("heartbeat: what is the current system state and next safe action?", aiwg_root=aiwg_root)
        mental_model = loop.get("mental_model_id", "")
        dialectic = loop.get("dialectical_review", {})
        quality_gate = loop.get("quality_gate", {})
        evidence.append(".aiwg/reports/metacognitive_loop_latest.json")
    except Exception as e:
        loop = {}
        mental_model = ""
        dialectic = _load(reports / "dialectical_review_latest.json")
        quality_gate = _load(reports / "metacognitive_quality_gate_latest.json")
        warnings.append(f"metacognitive_loop_degraded: {e}")

    # ---- STEP 7: SELF-IMPROVEMENT QUEUE ----
    si_queue = _load(reports / "self_improvement_action_queue.json")
    evidence.append(".aiwg/reports/self_improvement_action_queue.json")

    # ---- STEP 8: DECISION POLICY ----
    try:
        from heartbeat_decision_policy import select_next_action
        policy = select_next_action(aiwg_root=aiwg_root)
        selected_action = policy.selected_action
        dispatch = policy.dispatch_recommendation
        blocked = policy.blocked_actions
        warnings.extend(policy.warnings)
        evidence.append(".aiwg/reports/heartbeat_decision_policy_latest.json")
    except Exception as e:
        selected_action = {"action_type": "review_system_state", "priority": "medium", "status": "proposed"}
        dispatch = "human_review"
        blocked = ["autonomous_scaling"]
        warnings.append(f"decision_policy_degraded: {e}")

    # ---- STEP 9: OUTCOME ----
    # Decision logic
    hb_decision = "PASS_WITH_WARNINGS"
    if quality_gate.get("decision") == "FAIL":
        hb_decision = "FAIL"
    if kuzu_degraded:
        if hb_decision == "PASS":
            hb_decision = "PASS_WITH_WARNINGS"
    if selected_action.get("action_type") in ("repair_kuzu_persistence", "repair_kuzu_ready_truth") and dispatch in ("antigravity", "human_review"):
        hb_decision = "NEEDS_HUMAN_REVIEW"

    # ---- STEP 10: LEARNING EPISODE ----
    learning_ref = "DEGRADED_NOT_RECORDED"
    try:
        from session_store import SessionStore
        store = SessionStore(aiwg_root.resolve().parent)
        try:
            store.load_session("CURRENT")
        except FileNotFoundError:
            store.create_session("CURRENT", {"description": "Heartbeat session"})
        episode = {
            "heartbeat_id": hb_id,
            "selected_action": selected_action.get("action_type", ""),
            "why_selected": f"Highest priority non-blocked action from whole-body repair or self-improvement queues",
            "blocked_actions": blocked,
            "evidence_refs": evidence[:5],
            "warnings": warnings[:5],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        store.append_learning_episode("CURRENT", episode)
        learning_ref = f"sessions/CURRENT/learning_episodes (heartbeat {hb_id})"
    except Exception as e:
        warnings.append(f"learning_episode_not_recorded: {e}")

    # ---- STEP 11: NEXT HEARTBEAT SEED ----
    next_seed = {
        "previous_heartbeat_id": hb_id,
        "previous_decision": hb_decision,
        "next_action": selected_action.get("action_type", "review_system_state"),
        "dispatch": dispatch,
        "blocked_actions": blocked,
        "kuzu_degraded": kuzu_degraded,
        "quarantined_models": truth_hygiene.get("summary", {}).get("quarantined_count", 0),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # ---- BUILD OUTCOME ----
    outcome = HeartbeatOutcome(
        heartbeat_id=hb_id,
        mode=mode,
        decision=hb_decision,
        observation=observation_dict,
        truth_hygiene={"decision": truth_hygiene.get("decision", ""), "summary": truth_hygiene.get("summary", {})},
        epistemic_state={"decision": epistemic.get("decision", ""), "confidence": epistemic.get("confidence", 0)},
        bias_report={"decision": bias.get("decision", ""), "findings_count": len(bias.get("findings", []))},
        memory_spine={"status": memory_spine.get("status", ""), "graph_status": memory_spine.get("graph_status", "")},
        mental_model={"model_id": mental_model} if isinstance(mental_model, str) else mental_model,
        dialectic=dialectic,
        quality_gate={"decision": quality_gate.get("decision", ""), "quality_score": quality_gate.get("quality_score", 0)},
        self_improvement_queue={"actions_count": len(si_queue.get("actions", [])), "next": si_queue.get("next", "")},
        selected_action=selected_action,
        blocked_actions=blocked,
        dispatch_recommendation=dispatch,
        outcome_ref=f".aiwg/reports/heartbeat_latest.json",
        learning_episode_ref=learning_ref,
        next_heartbeat_seed=next_seed,
        warnings=warnings,
        evidence_refs=evidence,
        created_at=datetime.now(timezone.utc).isoformat(),
        circulation_summary=circulation_summary,
        dependency_reality=dependency_reality,
        degraded_capabilities=degraded_capabilities,
        toolchain_probe=toolchain_probe,
        runtime_closure_plan=runtime_closure_plan,
    )

    result = outcome.to_dict()

    # ---- WRITE OUTPUTS ----
    (reports / "heartbeat_latest.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (reports / "heartbeat_latest.md").write_text(
        f"# Heartbeat {hb_id}\n\n"
        f"Mode: {mode}\n"
        f"Decision: {hb_decision}\n"
        f"Selected: {selected_action.get('action_type', 'none')}\n"
        f"Dispatch: {dispatch}\n"
        f"Kuzu: {'DEGRADED' if kuzu_degraded else 'OK'}\n"
        f"Warnings: {len(warnings)}\n",
        encoding="utf-8")

    # Store in heartbeat state
    from heartbeat_state_store import HeartbeatStateStore
    state_store = HeartbeatStateStore(aiwg_root=aiwg_root)
    state_store.append_heartbeat(result)
    state_store.write_next_seed(next_seed)

    return result


if __name__ == "__main__":
    mode_arg = sys.argv[1] if len(sys.argv) > 1 else "observe_only"
    res = run_heartbeat(mode=mode_arg)
    print(json.dumps(res, indent=2))
