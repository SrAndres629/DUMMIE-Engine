from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class AutonomousRuntimeDecision:
    runtime_id: str
    phase: str
    decision: str  # continue_with_next_phase|repair_before_next_phase|request_human_review|request_authorization|block_due_to_safety|block_due_to_regression|complete_plan_v1_review
    recommended_next_action: str = ""
    can_execute_now: bool = False
    requires_human_or_orchestrator_authorization: bool = True
    selected_next_node: dict[str, Any] = field(default_factory=dict)
    permission_request: dict[str, Any] = field(default_factory=dict)
    blocking_reasons: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    confidence: float = 0.0
    advisory_only_until_authorized: bool = True
    plan_v1_completion_status: str = "incomplete"  # complete|complete_with_warnings|incomplete
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AutonomousStrategicPartnerRuntime:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"
        self.evolution_root = self.aiwg_root / "evolution"

    def run_strategic_runtime(self) -> AutonomousRuntimeDecision:
        # Load all reports
        current_pos = self._load_json(self.evolution_root / "current_position.json")
        next_seed = self._load_json(self.evolution_root / "next_phase_seed.json")
        
        coherence = self._load_json(self.reports_root / "mission_coherence_guard_latest.json")
        swarm = self._load_json(self.reports_root / "strategic_partner_swarm_latest.json")
        debate = self._load_json(self.reports_root / "debate_review_latest.json")
        autonomy = self._load_json(self.reports_root / "mission_autonomy_contract_latest.json")
        workstation = self._load_json(self.reports_root / "trusted_workstation_mode_latest.json")
        chaos = self._load_json(self.reports_root / "chaos_regression_report_latest.json")
        next_node = self._load_json(self.reports_root / "next_executable_node_latest.json")

        blocking_reasons = []
        risk_flags = []
        
        # Governance Gate Analysis
        if chaos.get("decision") == "FAIL":
            blocking_reasons.append("chaos_regression_failure")
        if coherence.get("decision") == "FAIL":
            blocking_reasons.append("mission_coherence_failure")
        if debate.get("decision") == "block":
            blocking_reasons.append("debate_review_veto")
        if autonomy.get("decision") == "FAIL":
            blocking_reasons.append("autonomy_contract_violation")
        
        # Decision Logic
        if blocking_reasons:
            decision = "block_due_to_safety"
            recommended = "Fix reported safety/coherence issues before proceeding."
        elif debate.get("decision") in ["repair_before_next_phase", "request_human_review"]:
            decision = "request_human_review"
            recommended = "Human review required due to debate objections."
        elif next_seed.get("next_phase") == "PLAN_V1_COMPLETION_REVIEW":
            decision = "complete_plan_v1_review"
            recommended = "Plan V1 runtime evolution complete. Proceed to final review."
        else:
            decision = "continue_with_next_phase"
            recommended = f"Proceed with phase {next_seed.get('next_phase')} according to Mission DAG."

        # Completion Status
        # Simple heuristic: if we reached P31 and all gates pass/warn, it's complete
        completion_status = "complete" if not blocking_reasons else "incomplete"
        if blocking_reasons:
             risk_flags.extend(blocking_reasons)

        res = AutonomousRuntimeDecision(
            runtime_id="autonomous_strategic_partner_runtime",
            phase=str(current_pos.get("current_phase", "P31")),
            decision=decision,
            recommended_next_action=recommended,
            selected_next_node=next_node.get("next_node", {}),
            blocking_reasons=blocking_reasons,
            risk_flags=risk_flags,
            evidence_refs=[
                ".aiwg/reports/mission_coherence_guard_latest.json",
                ".aiwg/reports/strategic_partner_swarm_latest.json",
                ".aiwg/reports/debate_review_latest.json",
                ".aiwg/reports/mission_autonomy_contract_latest.json",
                ".aiwg/reports/trusted_workstation_mode_latest.json",
                ".aiwg/reports/chaos_regression_report_latest.json"
            ],
            confidence=swarm.get("confidence", 0.0),
            plan_v1_completion_status=completion_status,
            generated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        )

        return res

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def write_report(self, decision: AutonomousRuntimeDecision) -> None:
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "autonomous_strategic_partner_latest.json").write_text(
            json.dumps(decision.to_dict(), indent=2) + "\n", encoding="utf-8"
        )


def run_autonomous_strategic_partner_runtime(aiwg_root: str | Path = ".aiwg") -> AutonomousRuntimeDecision:
    runtime = AutonomousStrategicPartnerRuntime(aiwg_root=aiwg_root)
    decision = runtime.run_strategic_runtime()
    runtime.write_report(decision)
    return decision
