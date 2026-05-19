from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class DebateRoleOpinion:
    role: str
    claim: str
    evidence_refs: list[str] = field(default_factory=list)
    objections: list[str] = field(default_factory=list)
    counterarguments: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    recommended_action: str = ""
    confidence: float = 1.0


@dataclass
class DebateReviewResult:
    debate_id: str
    phase: str
    mission_id: str
    decision: str  # accept_plan|accept_with_objections|repair_before_next_phase|request_human_review|block
    roles: list[DebateRoleOpinion] = field(default_factory=list)
    claims: list[str] = field(default_factory=list)
    objections: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    evidence_gaps: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    judge_verdict: dict[str, Any] = field(default_factory=dict)
    recommended_next_action: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    confidence: float = 0.0
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "debate_id": self.debate_id,
            "phase": self.phase,
            "mission_id": self.mission_id,
            "decision": self.decision,
            "roles": [asdict(r) for r in self.roles],
            "claims": self.claims,
            "objections": self.objections,
            "contradictions": self.contradictions,
            "evidence_gaps": self.evidence_gaps,
            "risk_flags": self.risk_flags,
            "judge_verdict": self.judge_verdict,
            "recommended_next_action": self.recommended_next_action,
            "evidence_refs": self.evidence_refs,
            "confidence": self.confidence,
            "generated_at": self.generated_at,
        }


class DebateReviewRuntime:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"
        self.evolution_root = self.aiwg_root / "evolution"

    def run_debate(self) -> DebateReviewResult:
        current_pos = self._load_json(self.evolution_root / "current_position.json")
        next_seed = self._load_json(self.evolution_root / "next_phase_seed.json")
        mission_plan = self._load_json(self.reports_root / "mission_plan_latest.json")
        swarm_output = self._load_json(self.reports_root / "strategic_partner_swarm_latest.json")
        coherence = self._load_json(self.reports_root / "mission_coherence_guard_latest.json")
        
        phase = str(current_pos.get("current_phase", "unknown"))
        next_phase = str(next_seed.get("next_phase", "unknown"))
        mission_id = f"MISSION_{next_phase}"

        # Roles implementations
        roles = [
            self._opinion_proposer(mission_plan),
            self._opinion_skeptic(mission_plan, swarm_output),
            self._opinion_evidence_auditor(coherence),
            self._opinion_risk_challenger(mission_plan, swarm_output),
            self._opinion_implementation_reviewer(mission_plan),
            self._opinion_mentor_judge(coherence, swarm_output),
        ]

        # Aggregation
        objections = sum([r.objections for r in roles], [])
        claims = [r.claim for r in roles]
        risk_flags = list(set(sum([r.risk_flags for r in roles], [])))
        evidence_gaps = []
        if not mission_plan: evidence_gaps.append("missing_mission_plan")
        if not swarm_output: evidence_gaps.append("missing_swarm_output")

        # Judge Verdict
        verdict_role = next(r for r in roles if r.role == "mentor_judge")
        decision = self._resolve_decision(verdict_role, coherence)

        res = DebateReviewResult(
            debate_id="debate_review_runtime",
            phase=phase,
            mission_id=mission_id,
            decision=decision,
            roles=roles,
            claims=claims,
            objections=objections,
            contradictions=[], # MVP simple contradiction detection can be added here
            evidence_gaps=evidence_gaps,
            risk_flags=risk_flags,
            judge_verdict={
                "verdict": verdict_role.recommended_action,
                "reason": verdict_role.claim,
                "allowed_to_continue": decision in ["accept_plan", "accept_with_objections"]
            },
            recommended_next_action=verdict_role.recommended_action,
            evidence_refs=[".aiwg/reports/mission_plan_latest.json", ".aiwg/reports/strategic_partner_swarm_latest.json"],
            confidence=sum(r.confidence for r in roles) / len(roles),
            generated_at=self._utc_now()
        )

        return res

    def _opinion_proposer(self, plan: dict) -> DebateRoleOpinion:
        return DebateRoleOpinion(
            role="proposer",
            claim=f"Mission {plan.get('mission_id')} is ready for execution",
            confidence=0.9
        )

    def _opinion_skeptic(self, plan: dict, swarm: dict) -> DebateRoleOpinion:
        obj = []
        if swarm.get("confidence", 1.0) > 0.95:
             obj.append("consensus_bias_risk: swarm confidence too high without dissent")
        return DebateRoleOpinion(
            role="skeptic",
            claim="Challenging mission assumptions",
            objections=obj,
            confidence=0.8
        )

    def _opinion_evidence_auditor(self, coherence: dict) -> DebateRoleOpinion:
        obj = []
        if coherence.get("decision") != "PASS":
            obj.append("physical_evidence_mismatch: mission artifacts not coherent with roadmap")
        return DebateRoleOpinion(
            role="evidence_auditor",
            claim="Verifying evidence grounding",
            objections=obj
        )

    def _opinion_risk_challenger(self, plan: dict, swarm: dict) -> DebateRoleOpinion:
        risks = swarm.get("risk_flags", [])
        return DebateRoleOpinion(
            role="risk_challenger",
            claim="Auditing operational risks",
            risk_flags=risks
        )

    def _opinion_implementation_reviewer(self, plan: dict) -> DebateRoleOpinion:
        obj = []
        for l3 in plan.get("l3_microphases", []):
            if not l3.get("tests_to_run"):
                obj.append(f"missing_tests: microphase {l3.get('microphase_id')} lacks test paths")
        return DebateRoleOpinion(
            role="implementation_reviewer",
            claim="Reviewing SDD/TDD compliance",
            objections=obj
        )

    def _opinion_mentor_judge(self, coherence: dict, swarm: dict) -> DebateRoleOpinion:
        if coherence.get("decision") == "FAIL":
            return DebateRoleOpinion(role="mentor_judge", claim="Blocking due to coherence failure", recommended_action="block")
        if swarm.get("decision") == "block_due_to_coherence_failure":
            return DebateRoleOpinion(role="mentor_judge", claim="Swarm blocked execution", recommended_action="block")
        
        return DebateRoleOpinion(
            role="mentor_judge",
            claim="Plan accepted with minor observations",
            recommended_action="accept_with_objections" if swarm.get("risk_flags") else "accept_plan"
        )

    def _resolve_decision(self, judge: DebateRoleOpinion, coherence: dict) -> str:
        if judge.recommended_action == "block": return "block"
        if coherence.get("decision") == "FAIL": return "repair_before_next_phase"
        return judge.recommended_action

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def write_report(self, result: DebateReviewResult) -> None:
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "debate_review_latest.json").write_text(
            json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8"
        )


def run_debate_review(aiwg_root: str | Path = ".aiwg") -> DebateReviewResult:
    runtime = DebateReviewRuntime(aiwg_root=aiwg_root)
    result = runtime.run_debate()
    runtime.write_report(result)
    return result
