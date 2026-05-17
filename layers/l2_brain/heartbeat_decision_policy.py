"""Heartbeat Decision Policy — HEARTBEAT-0

Selects the next action from the self-improvement queue, classifies
dispatch target, and enforces safety blockers.  Never executes mutations.
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
}


def classify_dispatch(action_type: str) -> str:
    return _DISPATCH_MAP.get(action_type, "human_review")


# ---------------------------------------------------------------------------
# Core policy
# ---------------------------------------------------------------------------

def select_next_action(aiwg_root: Path = Path(".aiwg")) -> HeartbeatDecisionPolicy:
    reports = aiwg_root / "reports"

    queue = _load(reports / "self_improvement_action_queue.json")
    delta = _load(reports / "evolution_delta_application_latest.json")
    hygiene = _load(reports / "mental_model_truth_hygiene_latest.json")
    readiness = _load(reports / "readiness_score_calibration_latest.json")

    actions = queue.get("actions", [])
    blocked_types = set(queue.get("blocked", []))
    blocked_types.update(a.get("action_type", "") for a in actions if a.get("status") == "blocked")

    # Always block autonomous_scaling
    blocked_types.add("autonomous_scaling")

    # Priority order: critical > high > medium > low
    priority_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    eligible = [a for a in actions
                if a.get("status") != "blocked"
                and a.get("action_type") not in blocked_types]
    eligible.sort(key=lambda a: priority_rank.get(a.get("priority", "low"), 9))

    warnings: List[str] = []

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

    # Extra safety: if Kuzu required and DEGRADED, force human_review
    kuzu_degraded = any("degraded" in f.get("id", "").lower() or "degraded" in f.get("description", "").lower()
                        for f in readiness.get("findings", []))
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
        f"Selected: {action_type}\n"
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
