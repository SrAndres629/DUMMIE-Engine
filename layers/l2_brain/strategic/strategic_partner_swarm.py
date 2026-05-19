from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class SwarmAgentOpinion:
    role: str
    claim: str
    evidence_refs: list[str] = field(default_factory=list)
    objections: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    confidence: float = 1.0
    decision: str = "PASS"


@dataclass
class SwarmDecision:
    swarm_id: str
    phase: str
    mission_id: str
    decision: str  # continue_next_phase|repair_before_next_phase|request_human_review|block_due_to_coherence_failure
    roles: list[SwarmAgentOpinion] = field(default_factory=list)
    consensus: dict[str, Any] = field(default_factory=dict)
    dissent: list[str] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)
    recommended_next_action: str = ""
    required_tests_next: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    confidence: float = 0.0
    advisory_only: bool = True
    can_modify_workspace: bool = False
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "swarm_id": self.swarm_id,
            "phase": self.phase,
            "mission_id": self.mission_id,
            "decision": self.decision,
            "roles": [asdict(r) for r in self.roles],
            "consensus": self.consensus,
            "dissent": self.dissent,
            "blocking_reasons": self.blocking_reasons,
            "recommended_next_action": self.recommended_next_action,
            "required_tests_next": self.required_tests_next,
            "evidence_refs": self.evidence_refs,
            "risk_flags": self.risk_flags,
            "confidence": self.confidence,
            "advisory_only": self.advisory_only,
            "can_modify_workspace": self.can_modify_workspace,
            "generated_at": self.generated_at,
        }


class StrategicPartnerSwarm:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"
        self.evolution_root = self.aiwg_root / "evolution"

    def run_swarm(self) -> SwarmDecision:
        current_pos = self._load_json(self.evolution_root / "current_position.json")
        next_seed = self._load_json(self.evolution_root / "next_phase_seed.json")
        mission_coherence = self._load_json(self.reports_root / "mission_coherence_guard_latest.json")
        
        phase = str(current_pos.get("current_phase", "unknown"))
        next_phase = str(next_seed.get("next_phase", "unknown"))
        mission_id = f"MISSION_{next_phase}"

        # Roles implementations (deterministic advisory)
        roles = [
            self._opinion_planner(next_seed),
            self._opinion_critic(mission_coherence),
            self._opinion_validator(mission_coherence),
            self._opinion_mentor(current_pos),
            self._opinion_risk_officer(next_seed, mission_coherence),
            self._opinion_execution_advisor(mission_coherence),
        ]

        # Consensus logic
        blocking = [r.role for r in roles if r.decision == "FAIL"]
        if mission_coherence.get("decision") == "FAIL":
            decision = "block_due_to_coherence_failure"
            recommended = "Regenerate mission plan and DAG to match canonical state"
        elif blocking:
            decision = "repair_before_next_phase"
            recommended = f"Review objections from roles: {', '.join(blocking)}"
        else:
            decision = "continue_next_phase"
            recommended = f"Proceed with {next_phase} following the mission DAG"

        swarm_res = SwarmDecision(
            swarm_id="strategic_partner_swarm",
            phase=phase,
            mission_id=mission_id,
            decision=decision,
            roles=roles,
            consensus={"overall": decision},
            blocking_reasons=[f"Role {r.role} objected: {r.objections}" for r in roles if r.objections],
            recommended_next_action=recommended,
            generated_at=self._utc_now()
        )
        
        # Aggregate stats
        swarm_res.confidence = sum(r.confidence for r in roles) / len(roles)
        swarm_res.risk_flags = list(set(sum([r.risk_flags for r in roles], [])))
        swarm_res.evidence_refs = [".aiwg/evolution/current_position.json", ".aiwg/evolution/next_phase_seed.json"]

        return swarm_res

    def _opinion_planner(self, seed: dict) -> SwarmAgentOpinion:
        return SwarmAgentOpinion(
            role="planner",
            claim=f"Mission for {seed.get('next_phase')} is structured as L1/L2/L3",
            recommendations=[f"Execute {len(seed.get('required_outputs', []))} phases"]
        )

    def _opinion_critic(self, coherence: dict) -> SwarmAgentOpinion:
        obj = []
        decision = "PASS"
        if coherence.get("decision") == "FAIL":
            obj.append("Mission artifacts are stale or inconsistent with roadmap")
            decision = "FAIL"
        return SwarmAgentOpinion(
            role="critic",
            claim="Analyzing internal mission coherence",
            objections=obj,
            decision=decision
        )

    def _opinion_validator(self, coherence: dict) -> SwarmAgentOpinion:
        return SwarmAgentOpinion(
            role="validator",
            claim="Verification of DAG structure and dependencies",
            decision="PASS" if coherence.get("decision") != "FAIL" else "FAIL"
        )

    def _opinion_mentor(self, current: dict) -> SwarmAgentOpinion:
        return SwarmAgentOpinion(
            role="mentor",
            claim=f"Steady progress in block {current.get('current_block')}",
            recommendations=["Maintain SDD/TDD rigor"]
        )

    def _opinion_risk_officer(self, seed: dict, coherence: dict) -> SwarmAgentOpinion:
        risks = []
        if coherence.get("decision") == "FAIL":
            risks.append("state_drift_detected")
        if not seed.get("success_conditions"):
            risks.append("missing_success_metrics")
        return SwarmAgentOpinion(
            role="risk_officer",
            claim="Evaluating operational risks",
            risk_flags=risks
        )

    def _opinion_execution_advisor(self, coherence: dict) -> SwarmAgentOpinion:
        return SwarmAgentOpinion(
            role="execution_advisor",
            claim="Checking readiness for first node execution",
            decision="PASS" if coherence.get("decision") == "PASS" else "FAIL"
        )

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def write_swarm_output(self, decision: SwarmDecision) -> None:
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "strategic_partner_swarm_latest.json").write_text(
            json.dumps(decision.to_dict(), indent=2) + "\n", encoding="utf-8"
        )


def run_strategic_partner_swarm(aiwg_root: str | Path = ".aiwg") -> SwarmDecision:
    swarm = StrategicPartnerSwarm(aiwg_root=aiwg_root)
    decision = swarm.run_swarm()
    swarm.write_swarm_output(decision)
    return decision
