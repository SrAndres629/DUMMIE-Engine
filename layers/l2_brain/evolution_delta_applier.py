"""Evolution Delta Applier — Pack 5.2.2

Transforms philosophical evolution deltas into prioritised, actionable
improvement items.  Never performs mutations itself — only proposes.
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class EvolutionDeltaAction:
    action_id: str
    source_delta: str
    action_type: str
    priority: str       # low | medium | high | critical
    blocks_autonomy: bool
    blocks_daily_use: bool
    evidence_refs: List[str]
    recommended_pack: str
    status: str         # proposed | accepted | blocked | done


@dataclass
class EvolutionDeltaApplication:
    decision: str       # PASS | PASS_WITH_WARNINGS | FAIL
    actions: List[Dict[str, Any]]
    blocked_actions: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Source readers
# ---------------------------------------------------------------------------

def _load(path: Path) -> Dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def apply_evolution_delta(aiwg_root: Path = Path(".aiwg")) -> Dict[str, Any]:
    reports = aiwg_root / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    delta = _load(reports / "metacognitive_evolution_delta_latest.json")
    bias = _load(reports / "cognitive_bias_report_latest.json")
    hygiene = _load(reports / "mental_model_truth_hygiene_latest.json")
    repair = _load(reports / "pack_5_2_1_closure_integrity_repair.json")

    actions: List[EvolutionDeltaAction] = []
    blocked: List[str] = []

    # --- 1. From evolution delta: next_check_recommended ----------------
    next_check = delta.get("next_check_recommended", "")
    if next_check:
        priority = "critical" if "kuzu" in next_check else "high"
        blocks_auto = "kuzu" in next_check or "memory" in next_check
        actions.append(EvolutionDeltaAction(
            action_id=f"eda-{uuid.uuid4().hex[:8]}",
            source_delta="metacognitive_evolution_delta_latest.json",
            action_type=next_check,
            priority=priority,
            blocks_autonomy=blocks_auto,
            blocks_daily_use=False,
            evidence_refs=[".aiwg/reports/metacognitive_evolution_delta_latest.json"],
            recommended_pack="PACK_5_3_KUZU_REPAIR" if "kuzu" in next_check else "PACK_5_3",
            status="proposed",
        ))
        if blocks_auto:
            blocked.append(next_check)

    # --- 2. From hygiene: quarantined models ----------------------------
    quarantined_count = hygiene.get("summary", {}).get("quarantined_count", 0)
    if quarantined_count > 0:
        actions.append(EvolutionDeltaAction(
            action_id=f"eda-{uuid.uuid4().hex[:8]}",
            source_delta="mental_model_truth_hygiene_latest.json",
            action_type="quarantine_overconfident_models",
            priority="high",
            blocks_autonomy=True,
            blocks_daily_use=False,
            evidence_refs=[".aiwg/reports/mental_model_truth_hygiene_latest.json"],
            recommended_pack="PACK_5_2_2",
            status="proposed",
        ))
        blocked.append("quarantine_overconfident_models")

    # --- 3. From bias: premature scaling --------------------------------
    bias_findings = bias.get("findings", [])
    if bias_findings:
        actions.append(EvolutionDeltaAction(
            action_id=f"eda-{uuid.uuid4().hex[:8]}",
            source_delta="cognitive_bias_report_latest.json",
            action_type="block_autonomous_scaling",
            priority="critical",
            blocks_autonomy=True,
            blocks_daily_use=False,
            evidence_refs=[".aiwg/reports/cognitive_bias_report_latest.json"],
            recommended_pack="PACK_5_3",
            status="blocked",
        ))
        blocked.append("autonomous_scaling")

    # --- 4. Increase test coverage (always if we detect test debt) ------
    needs_review = hygiene.get("summary", {}).get("needs_review_count", 0)
    if needs_review > 0:
        actions.append(EvolutionDeltaAction(
            action_id=f"eda-{uuid.uuid4().hex[:8]}",
            source_delta="mental_model_truth_hygiene_latest.json",
            action_type="increase_test_coverage",
            priority="high",
            blocks_autonomy=True,
            blocks_daily_use=False,
            evidence_refs=[".aiwg/reports/mental_model_truth_hygiene_latest.json"],
            recommended_pack="PACK_5_3",
            status="proposed",
        ))

    # --- 5. Wire memory spine ------------------------------------------
    if delta.get("revision_type") == "humility_calibration":
        actions.append(EvolutionDeltaAction(
            action_id=f"eda-{uuid.uuid4().hex[:8]}",
            source_delta="metacognitive_evolution_delta_latest.json",
            action_type="wire_memory_spine_to_entrypoints",
            priority="medium",
            blocks_autonomy=False,
            blocks_daily_use=False,
            evidence_refs=[".aiwg/reports/metacognitive_evolution_delta_latest.json"],
            recommended_pack="PACK_5_3",
            status="proposed",
        ))

    # --- 6. Run truth hygiene before planning (always) ------------------
    actions.append(EvolutionDeltaAction(
        action_id=f"eda-{uuid.uuid4().hex[:8]}",
        source_delta="self_improvement_policy",
        action_type="run_truth_hygiene_before_planning",
        priority="medium",
        blocks_autonomy=False,
        blocks_daily_use=False,
        evidence_refs=[],
        recommended_pack="ONGOING",
        status="proposed",
    ))

    # --- 7. Autonomous scaling sentinel (always blocked while degraded) -
    actions.append(EvolutionDeltaAction(
        action_id=f"eda-{uuid.uuid4().hex[:8]}",
        source_delta="system_policy",
        action_type="autonomous_scaling",
        priority="critical",
        blocks_autonomy=True,
        blocks_daily_use=False,
        evidence_refs=[
            ".aiwg/reports/readiness_score_calibration_latest.json",
            ".aiwg/reports/mental_model_truth_hygiene_latest.json",
        ],
        recommended_pack="PACK_5_3_KUZU_REPAIR",
        status="blocked",
    ))
    blocked.append("autonomous_scaling")

    # Determine decision -----------------------------------------------
    has_critical = any(a.priority == "critical" for a in actions)
    decision = "PASS_WITH_WARNINGS" if has_critical else "PASS"

    result = EvolutionDeltaApplication(
        decision=decision,
        actions=[asdict(a) for a in actions],
        blocked_actions=list(set(blocked)),
    )

    # Write outputs ----------------------------------------------------
    (reports / "evolution_delta_application_latest.json").write_text(
        json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    (reports / "evolution_delta_application_latest.md").write_text(
        f"# Evolution Delta Application\n\nDecision: {decision}\n"
        f"Actions: {len(actions)}\nBlocked: {', '.join(set(blocked)) or 'none'}\n",
        encoding="utf-8")

    return result.to_dict()


if __name__ == "__main__":
    print(json.dumps(apply_evolution_delta(), indent=2))
