from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class MissionMicroPhase:
    microphase_id: str
    parent_phase_id: str
    title: str
    action: str
    expected_file_changes: list[str] = field(default_factory=list)
    tests_to_run: list[str] = field(default_factory=list)
    validation_commands: list[str] = field(default_factory=list)
    rollback_notes: str = ""
    done_criteria: str = ""


@dataclass
class MissionPhase:
    phase_id: str
    title: str
    purpose: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    required_specs: list[str] = field(default_factory=list)
    required_tests: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)


@dataclass
class MissionPlan:
    mission_id: str
    objective: str
    source_phase: str
    current_phase: str
    next_phase: str
    l1_goal: dict[str, Any] = field(default_factory=dict)
    l2_phases: list[MissionPhase] = field(default_factory=list)
    l3_microphases: list[MissionMicroPhase] = field(default_factory=list)
    sdd_requirements: list[str] = field(default_factory=list)
    tdd_requirements: list[str] = field(default_factory=list)
    evidence_requirements: list[str] = field(default_factory=list)
    risk_register: list[str] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)
    decision: str = "PASS"
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "objective": self.objective,
            "source_phase": self.source_phase,
            "current_phase": self.current_phase,
            "next_phase": self.next_phase,
            "l1_goal": self.l1_goal,
            "l2_phases": [asdict(p) for p in self.l2_phases],
            "l3_microphases": [asdict(m) for m in self.l3_microphases],
            "sdd_requirements": self.sdd_requirements,
            "tdd_requirements": self.tdd_requirements,
            "evidence_requirements": self.evidence_requirements,
            "risk_register": self.risk_register,
            "blocked_actions": self.blocked_actions,
            "decision": self.decision,
            "generated_at": self.generated_at,
        }


class MissionPlanner:
    def __init__(self, root: str | Path = "."):
        self.root = Path(root)
        self.aiwg_root = self.root / ".aiwg"
        self.reports_root = self.aiwg_root / "reports"

    def create_mission_plan(self) -> MissionPlan:
        # Load inputs
        current_pos = self._load_json(self.aiwg_root / "evolution" / "current_position.json")
        next_seed = self._load_json(self.aiwg_root / "evolution" / "next_phase_seed.json")
        repo_probe = self._load_json(self.reports_root / "repo_probe_latest.json")

        mission_id = f"MISSION_{next_seed.get('next_phase', 'UNKNOWN')}"
        objective = next_seed.get("objective", "Execute next evolutionary step")
        
        # L1 Goal
        l1_goal = {
            "title": next_seed.get("name", "Unknown Phase"),
            "success_conditions": next_seed.get("success_conditions", [])
        }

        # Mock L2 and L3 planning based on next_seed required_outputs
        l2_phases = []
        l3_microphases = []
        
        outputs = next_seed.get("required_outputs", [])
        for i, out in enumerate(outputs):
            phase_id = f"L2_{i+1}"
            l2 = MissionPhase(
                phase_id=phase_id,
                title=f"Produce {out}",
                purpose=f"Implement and verify {out}",
                outputs=[out],
                acceptance_criteria=[f"File {out} exists", f"Tests for {out} pass"]
            )
            l2_phases.append(l2)
            
            # Microphases
            l3_microphases.append(MissionMicroPhase(
                microphase_id=f"{phase_id}_M1",
                parent_phase_id=phase_id,
                title=f"Draft {out}",
                action=f"Create/Update {out}",
                expected_file_changes=[out]
            ))
            l3_microphases.append(MissionMicroPhase(
                microphase_id=f"{phase_id}_M2",
                parent_phase_id=phase_id,
                title=f"Verify {out}",
                action=f"Run tests for {out}",
                tests_to_run=[f"tests/test_{Path(out).stem}.py"]
            ))

        plan = MissionPlan(
            mission_id=mission_id,
            objective=objective,
            source_phase=str(current_pos.get("current_phase", "P24")),
            current_phase=str(current_pos.get("current_phase", "P24")),
            next_phase=str(next_seed.get("next_phase", "P25")),
            l1_goal=l1_goal,
            l2_phases=l2_phases,
            l3_microphases=l3_microphases,
            sdd_requirements=["SDD: Every change must have a spec triplet", "SDD: No runtime without spec"],
            tdd_requirements=["TDD: Every runtime module must have matching tests", "TDD: Tests must pass before commit"],
            evidence_requirements=["Repo probe must reflect changes", "Latest outputs must be coherent"],
            generated_at=self._utc_now()
        )

        return plan

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def write_plan(self, plan: MissionPlan) -> None:
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "mission_plan_latest.json").write_text(
            json.dumps(plan.to_dict(), indent=2) + "\n", encoding="utf-8"
        )
        
        md_content = self.render_md(plan)
        (self.reports_root / "mission_plan_latest.md").write_text(md_content, encoding="utf-8")

    def render_md(self, plan: MissionPlan) -> str:
        lines = [
            f"# Mission Plan: {plan.mission_id}",
            f"**Objective:** {plan.objective}",
            f"**Generated at:** {plan.generated_at}",
            "",
            "## L1 Goal",
            f"### {plan.l1_goal.get('title')}",
            "**Success Conditions:**",
            *[f"- {c}" for c in plan.l1_goal.get("success_conditions", [])],
            "",
            "## L2 Phases",
        ]
        for l2 in plan.l2_phases:
            lines.append(f"### {l2.phase_id}: {l2.title}")
            lines.append(f"- **Purpose:** {l2.purpose}")
            lines.append("- **Acceptance Criteria:**")
            for ac in l2.acceptance_criteria:
                lines.append(f"  - {ac}")
        
        lines.append("\n## SDD/TDD Requirements")
        for req in plan.sdd_requirements:
            lines.append(f"- {req}")
        for req in plan.tdd_requirements:
            lines.append(f"- {req}")
            
        return "\n".join(lines)


def create_mission_plan(root: str | Path = ".") -> MissionPlan:
    planner = MissionPlanner(root=root)
    plan = planner.create_mission_plan()
    planner.write_plan(plan)
    return plan


if __name__ == "__main__":
    plan = create_mission_plan()
    print(f"Created mission plan {plan.mission_id}")
