# Spec: 160_metacognitive_evolution_flywheel
# Spec: DE-V2-L2-160
"""Metacognitive Evolution Flywheel — Hardened for Pack 5.2.2

Now consumes truth hygiene and evolution delta to produce action revisions,
model hygiene summaries and blocked action lists alongside belief revision.
"""

import uuid
import json
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Any, List


@dataclass
class MetacognitiveEvolutionFlywheel:
    decision: str
    step_id: str
    evolution_delta: Dict[str, Any]
    belief_revision: str = ""
    action_revision: str = ""
    model_hygiene_summary: Dict[str, Any] = field(default_factory=dict)
    next_self_improvement_action: str = ""
    blocked_actions: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self): return asdict(self)


def _load(path: Path) -> Dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def run_metacognitive_evolution_flywheel(intent: str, aiwg_root: Path = Path(".aiwg"), mode: str = "full") -> MetacognitiveEvolutionFlywheel:
    step_id = f"flywheel-{uuid.uuid4().hex[:8]}"
    reports = aiwg_root / "reports"

    # Base delta
    delta = {
        "belief_changed": "From 'System is ready' to 'System has epistemic debt'",
        "evidence_source": "readiness_score_calibration_latest.json",
        "revision_type": "humility_calibration",
        "next_check_recommended": "repair_kuzu_persistence"
    }

    belief_revision = "System believed it was fully ready; evidence shows epistemic debt remains."
    action_revision = ""
    model_hygiene_summary: Dict[str, Any] = {}
    next_action = ""
    blocked: List[str] = []

    if mode == "full":
        # Consume truth hygiene if available (avoid recursion with self_improvement_runtime)
        hygiene = _load(reports / "mental_model_truth_hygiene_latest.json")
        if hygiene:
            model_hygiene_summary = hygiene.get("summary", {})
            quarantined = model_hygiene_summary.get("quarantined_count", 0)
            if quarantined > 0:
                belief_revision += f" {quarantined} models were quarantined due to overconfidence."
                blocked.append("autonomous_scaling")

        # Consume evolution delta application
        delta_app = _load(reports / "evolution_delta_application_latest.json")
        if delta_app:
            app_actions = delta_app.get("actions", [])
            for a in app_actions:
                if a.get("status") == "blocked":
                    blocked.append(a.get("action_type", ""))
            # Pick next action
            for a in app_actions:
                if a.get("status") != "blocked":
                    next_action = a.get("action_type", "")
                    break
            action_revision = f"Next recommended action: {next_action}" if next_action else "No actionable items"

        # Consume self-improvement queue (observe_only to prevent recursion)
        si_queue = _load(reports / "self_improvement_action_queue.json")
        if si_queue:
            next_action = si_queue.get("next", next_action)
            for b in si_queue.get("blocked", []):
                if b not in blocked:
                    blocked.append(b)

    return MetacognitiveEvolutionFlywheel(
        decision="PASS",
        step_id=step_id,
        evolution_delta=delta,
        belief_revision=belief_revision,
        action_revision=action_revision,
        model_hygiene_summary=model_hygiene_summary,
        next_self_improvement_action=next_action,
        blocked_actions=list(set(blocked)),
    )
