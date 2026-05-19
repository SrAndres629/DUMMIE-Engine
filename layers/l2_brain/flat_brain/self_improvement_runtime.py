# Spec: 163_self_improvement_runtime
# Spec: DE-V2-L2-163
"""Self-Improvement Runtime — Pack 5.2.2

Orchestrates the full self-observation → hygiene → evolution → action queue
cycle.  Produces an evidence-based action queue and blocks premature scaling.
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class SelfImprovementCycle:
    decision: str       # PASS | PASS_WITH_WARNINGS | NEEDS_HUMAN_REVIEW | FAIL
    cycle_id: str
    hygiene_summary: Dict[str, Any]
    epistemic_summary: Dict[str, Any]
    bias_summary: Dict[str, Any]
    delta_summary: Dict[str, Any]
    action_queue: List[Dict[str, Any]]
    blocked_actions: List[str]
    next_self_improvement_action: str
    autonomous_scaling_blocked: bool
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load(path: Path) -> Dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def run_self_improvement_cycle(aiwg_root: Path = Path(".aiwg")) -> Dict[str, Any]:
    reports = aiwg_root / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    cycle_id = f"sic-{uuid.uuid4().hex[:8]}"

    # --- 1. Mental Model Truth Hygiene --------------------------------
    from mental_model_truth_hygiene import run_mental_model_truth_hygiene
    hygiene = run_mental_model_truth_hygiene(aiwg_root=aiwg_root)

    # --- 2. Epistemic State -------------------------------------------
    epistemic = _load(reports / "epistemic_state_latest.json")
    if not epistemic:
        try:
            from epistemic_state_runtime import build_epistemic_state
            ep = build_epistemic_state("self improvement cycle", aiwg_root=aiwg_root)
            epistemic = ep.to_dict()
            (reports / "epistemic_state_latest.json").write_text(
                json.dumps(epistemic, indent=2), encoding="utf-8")
        except Exception:
            epistemic = {"decision": "DEGRADED", "confidence": 0.0}

    # --- 3. Bias Detection --------------------------------------------
    bias = _load(reports / "cognitive_bias_report_latest.json")
    if not bias:
        try:
            from cognitive_bias_detector import detect_cognitive_biases
            b = detect_cognitive_biases("self improvement cycle", aiwg_root=aiwg_root)
            bias = b.to_dict() if hasattr(b, "to_dict") else b
            (reports / "cognitive_bias_report_latest.json").write_text(
                json.dumps(bias, indent=2), encoding="utf-8")
        except Exception:
            bias = {"decision": "DEGRADED", "findings": []}

    # --- 4. Evolution Delta Application --------------------------------
    from evolution_delta_applier import apply_evolution_delta
    delta = apply_evolution_delta(aiwg_root=aiwg_root)

    # --- 5. Dialectical Review of proposed next action -----------------
    dialectic = _load(reports / "dialectical_review_latest.json")

    # --- 6. Build action queue -----------------------------------------
    raw_actions = delta.get("actions", [])

    # Sort by priority: critical > high > medium > low
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_actions = sorted(raw_actions, key=lambda a: priority_order.get(a.get("priority", "low"), 9))

    blocked = delta.get("blocked_actions", [])

    # Determine next self-improvement action (first non-blocked proposed)
    next_action = ""
    for a in sorted_actions:
        if a.get("status") != "blocked" and a.get("action_type") not in blocked:
            next_action = a.get("action_type", "")
            break
    if not next_action and sorted_actions:
        next_action = sorted_actions[0].get("action_type", "review_system_state")

    # --- 7. Autonomous scaling check -----------------------------------
    autonomous_blocked = any(
        a.get("action_type") == "autonomous_scaling" and a.get("status") == "blocked"
        for a in sorted_actions
    )
    # Also check hygiene blockers
    quarantined_count = hygiene.get("summary", {}).get("quarantined_count", 0)
    if quarantined_count > 0:
        autonomous_blocked = True

    # --- 8. Decision logic ---------------------------------------------
    warnings: List[str] = []
    decision = "PASS"

    if autonomous_blocked:
        warnings.append("Autonomous scaling is BLOCKED until Kuzu repair and model hygiene cleanup")
        decision = "PASS_WITH_WARNINGS"

    if hygiene.get("decision") == "FAIL":
        decision = "FAIL"
        warnings.append("Mental model truth hygiene FAILED")

    if bias.get("decision") == "FAIL":
        decision = "NEEDS_HUMAN_REVIEW"
        warnings.append("Cognitive bias report is FAIL")

    ep_debts = epistemic.get("epistemic_debts", [])
    if ep_debts:
        warnings.append(f"Epistemic debts detected: {len(ep_debts)}")
        if decision == "PASS":
            decision = "PASS_WITH_WARNINGS"

    # --- 9. Build result -----------------------------------------------
    cycle = SelfImprovementCycle(
        decision=decision,
        cycle_id=cycle_id,
        hygiene_summary=hygiene.get("summary", {}),
        epistemic_summary={
            "decision": epistemic.get("decision", ""),
            "confidence": epistemic.get("confidence", 0),
            "debts": len(ep_debts),
        },
        bias_summary={
            "decision": bias.get("decision", ""),
            "findings_count": len(bias.get("findings", [])),
        },
        delta_summary={
            "decision": delta.get("decision", ""),
            "actions_count": len(sorted_actions),
            "blocked_count": len(blocked),
        },
        action_queue=sorted_actions,
        blocked_actions=list(set(blocked)),
        next_self_improvement_action=next_action,
        autonomous_scaling_blocked=autonomous_blocked,
        warnings=warnings,
    )

    result = cycle.to_dict()

    # --- 10. Write outputs ---------------------------------------------
    (reports / "self_improvement_cycle_latest.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8")
    (reports / "self_improvement_cycle_latest.md").write_text(
        f"# Self-Improvement Cycle\n\nDecision: {decision}\n"
        f"Next action: {next_action}\n"
        f"Autonomous scaling blocked: {autonomous_blocked}\n"
        f"Actions queued: {len(sorted_actions)}\n"
        f"Warnings: {len(warnings)}\n",
        encoding="utf-8")
    (reports / "self_improvement_action_queue.json").write_text(
        json.dumps({"actions": sorted_actions, "blocked": list(set(blocked)),
                     "next": next_action, "timestamp": cycle.timestamp}, indent=2),
        encoding="utf-8")

    return result


if __name__ == "__main__":
    print(json.dumps(run_self_improvement_cycle(), indent=2))
