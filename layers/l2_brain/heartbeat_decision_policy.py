"""Heartbeat Decision Policy — HEARTBEAT-2.1

Selects the next action from the self-improvement queue, classifies
dispatch target, and enforces safety blockers. Never executes mutations.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class HeartbeatDecisionPolicy:
    selected_action: Dict[str, Any]
    dispatch_recommendation: str   # local|antigravity|codex|gemini|human_review|none
    blocked_actions: List[str]
    reason: str
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


# ---------------------------------------------------------------------------
# Dispatch classification
# ---------------------------------------------------------------------------

_DISPATCH_MAP = {
    "repair_kuzu_persistence":       "antigravity",
    "increase_test_coverage":        "codex",
    "wire_memory_spine_to_entrypoints": "antigravity",
    "quarantine_overconfident_models": "local",
    "run_truth_hygiene_before_planning": "local",
    "block_autonomous_scaling":      "local",
    "generate_action_queue":         "local",
    "repair_scanner":                "antigravity",
    "build_wiring_matrix":           "local",
    "classify_shadow_modules":       "local",
    "resolve_dependency_first":      "antigravity",
}


def classify_dispatch(action_type: str) -> str:
    return _DISPATCH_MAP.get(action_type, "human_review")


# ---------------------------------------------------------------------------
# Core policy
# ---------------------------------------------------------------------------

def select_next_action(aiwg_root: Path = Path(".aiwg")) -> HeartbeatDecisionPolicy:
    reports = aiwg_root / "reports"

    queue = _load(reports / "self_improvement_action_queue.json")
    readiness = _load(reports / "readiness_score_calibration_latest.json")
    scan_latest = _load(reports / "whole_body_scan_latest.json")

    # Load 2.1 reality audit structures
    audit = _load(reports / "runtime_dependency_audit_latest.json")
    registry = _load(reports / "degraded_capability_registry_latest.json")
    tools = _load(reports / "environment_toolchain_probe_latest.json")
    closure = _load(reports / "runtime_closure_plan_latest.json")

    actions = queue.get("actions", [])
    blocked_types = set(queue.get("blocked", []))
    blocked_types.update(a.get("action_type", "") for a in actions if a.get("status") == "blocked")

    # Always block autonomous_scaling
    blocked_types.add("autonomous_scaling")

    # If systemic coherence score is under 60%, block autonomous scaling explicitly
    coherence_score = scan_latest.get("overall_coherence_score", 0.0)
    warnings: List[str] = []
    if coherence_score < 60.0:
        blocked_types.add("autonomous_execution")
        warnings.append(f"Systemic Coherence Score ({coherence_score}%) is under 60% — autonomous execution is strictly blocked.")

    # 1. Check Kùzu database status
    kuzu_cap = {}
    for c in registry.get("capabilities", []):
        if c.get("capability_id") == "kuzu_4dtes_persistence":
            kuzu_cap = c
            break

    kuzu_degraded = kuzu_cap.get("actual_status", "DEGRADED") in ("DEGRADED", "SIMULATED", "MISSING")
    
    if kuzu_degraded:
        # Enforce that if Kuzu is degraded, we block any action that relies on graph persistence, except repair
        blocked_types.add("graph_persistence_transaction_write")
        warnings.append("Kùzu DB 4D-TES Persistence is DEGRADED — graph-dependent actions are locked except repair.")

    # 2. Check Embeddings status
    embed_cap = {}
    for c in registry.get("capabilities", []):
        if c.get("capability_id") == "real_semantic_embeddings":
            embed_cap = c
            break

    if embed_cap.get("actual_status") == "FALLBACK":
        warnings.append("Real semantic retrieval is not ready; memory router operates under deterministic mock projection.")

    # 3. Check Daemon status
    daemon_cap = {}
    for c in registry.get("capabilities", []):
        if c.get("capability_id") == "daemon_persistent_runtime":
            daemon_cap = c
            break

    if daemon_cap.get("actual_status") == "SIMULATED":
        blocked_types.add("autonomous_runtime")
        warnings.append("Daemon background runtime is simulated — autonomous runtime claim is blocked.")

    # 4. Check Polyglot status
    missing_toolchains = tools.get("missing_toolchains", [])
    if missing_toolchains:
        warnings.append(f"Optional polyglot toolchains are missing: {', '.join(missing_toolchains)} — full operational readiness is disabled.")

    # Apply strict priority gates before queue evaluation
    # Rule 1: Missing core python libraries
    required_missing = audit.get("required_missing_dependencies", [])
    if required_missing:
        selected = {
            "action_id": "dep-repair",
            "action_type": "resolve_dependency_first",
            "priority": "critical",
            "status": "proposed"
        }
        dispatch = "antigravity"
        reason = f"Required python dependencies are missing: {', '.join(required_missing)}. Resolving them is critical."
    else:
        # Priority order: critical > high > medium > low
        priority_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        eligible = [a for a in actions
                    if a.get("status") != "blocked"
                    and a.get("action_type") not in blocked_types]
        eligible.sort(key=lambda a: priority_rank.get(a.get("priority", "low"), 9))

        if not eligible:
            # Fallback: generate_action_queue
            selected = {
                "action_id": "hb-fallback",
                "action_type": "generate_action_queue",
                "priority": "medium",
                "status": "proposed",
            }
            warnings.append("No eligible actions in queue; recommending action queue regeneration")
        else:
            selected = eligible[0]

        action_type = selected.get("action_type", "unknown")
        dispatch = classify_dispatch(action_type)

        if kuzu_degraded and action_type in ("repair_kuzu_persistence",):
            dispatch = "antigravity"
            warnings.append("Kuzu DEGRADED — repair requires implementation plan + human approval")

        reason = f"Selected '{action_type}' (priority={selected.get('priority')}) from self-improvement queue. Dispatch: {dispatch}."

    result = HeartbeatDecisionPolicy(
        selected_action=selected,
        dispatch_recommendation=dispatch,
        blocked_actions=sorted(blocked_types),
        reason=reason,
        warnings=warnings,
    )

    # Write output
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "heartbeat_decision_policy_latest.json").write_text(
        json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    (reports / "heartbeat_decision_policy_latest.md").write_text(
        f"# Heartbeat Decision Policy\n\n"
        f"Selected: {selected.get('action_type', 'unknown')}\n"
        f"Dispatch: {dispatch}\n"
        f"Blocked: {', '.join(sorted(blocked_types))}\n"
        f"Reason: {reason}\n",
        encoding="utf-8")

    return result


def block_unsafe_actions(actions: List[Dict[str, Any]]) -> List[str]:
    """Return list of action_types that must remain blocked."""
    blocked = []
    for a in actions:
        if a.get("action_type") == "autonomous_scaling":
            blocked.append("autonomous_scaling")
        if a.get("status") == "blocked":
            blocked.append(a.get("action_type", ""))
    return list(set(blocked))


if __name__ == "__main__":
    result = select_next_action()
    print(json.dumps(result.to_dict(), indent=2))
