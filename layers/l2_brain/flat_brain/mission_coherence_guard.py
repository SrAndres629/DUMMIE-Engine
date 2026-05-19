from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class MissionCoherenceFinding:
    artifact: str
    message: str
    expected: Any
    actual: Any
    severity: str  # ERROR|WARNING


@dataclass
class MissionCoherenceReport:
    decision: str  # PASS|PASS_WITH_WARNINGS|FAIL
    findings: list[MissionCoherenceFinding] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "findings": [asdict(f) for f in self.findings],
            "generated_at": self.generated_at,
        }


class MissionCoherenceGuard:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"
        self.evolution_root = self.aiwg_root / "evolution"

    def check_mission_coherence(self) -> MissionCoherenceReport:
        findings: list[MissionCoherenceFinding] = []

        current_pos = self._load_json(self.evolution_root / "current_position.json")
        next_seed = self._load_json(self.evolution_root / "next_phase_seed.json")

        if not current_pos or not next_seed:
            findings.append(MissionCoherenceFinding("canonical_state", "Missing current_position or next_phase_seed", "present", "missing", "ERROR"))
            return MissionCoherenceReport(decision="FAIL", findings=findings, generated_at=self._utc_now())

        expected_next_phase = str(next_seed.get("next_phase", "unknown"))
        expected_mission_id = f"MISSION_{expected_next_phase}"

        # Check Mission Plan
        plan_path = self.reports_root / "mission_plan_latest.json"
        if plan_path.exists():
            plan = self._load_json(plan_path)
            actual_mission_id = plan.get("mission_id")
            actual_next_phase = plan.get("next_phase")
            if actual_mission_id != expected_mission_id:
                findings.append(MissionCoherenceFinding("mission_plan_latest.json", "Mission ID mismatch", expected_mission_id, actual_mission_id, "ERROR"))
            if actual_next_phase != expected_next_phase:
                findings.append(MissionCoherenceFinding("mission_plan_latest.json", "Next phase mismatch", expected_next_phase, actual_next_phase, "ERROR"))
        else:
            findings.append(MissionCoherenceFinding("mission_plan_latest.json", "Missing", "present", "missing", "WARNING"))

        # Check DAG
        dag_path = self.reports_root / "mission_orchestrator_dag_latest.json"
        if dag_path.exists():
            dag = self._load_json(dag_path)
            actual_dag_mission_id = dag.get("mission_id")
            if actual_dag_mission_id != expected_mission_id:
                findings.append(MissionCoherenceFinding("mission_orchestrator_dag_latest.json", "Mission ID mismatch", expected_mission_id, actual_dag_mission_id, "ERROR"))
            
            # Check for invalid test paths (hardcoded heuristic for P25.1)
            nodes = dag.get("nodes", {})
            for node_id, node in nodes.items():
                tests = node.get("tests", [])
                for t in tests:
                    if "test_test_" in t:
                        findings.append(MissionCoherenceFinding(f"dag_node:{node_id}", "Invented test path detected", "valid_path", t, "ERROR"))
        else:
            findings.append(MissionCoherenceFinding("mission_orchestrator_dag_latest.json", "Missing", "present", "missing", "WARNING"))

        # Check Next Node
        next_node_path = self.reports_root / "next_executable_node_latest.json"
        if next_node_path.exists():
            next_node_data = self._load_json(next_node_path)
            node = next_node_data.get("next_node")
            if node:
                title = node.get("title", "")
                if expected_mission_id not in title and expected_next_phase not in title:
                    # Heuristic check on title if mission_id not directly in payload outside title
                    pass
        else:
            findings.append(MissionCoherenceFinding("next_executable_node_latest.json", "Missing", "present", "missing", "WARNING"))

        # Decision logic
        errors = [f for f in findings if f.severity == "ERROR"]
        warnings = [f for f in findings if f.severity == "WARNING"]

        if errors:
            decision = "FAIL"
        elif warnings:
            decision = "PASS_WITH_WARNINGS"
        else:
            decision = "PASS"

        return MissionCoherenceReport(decision=decision, findings=findings, generated_at=self._utc_now())

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def write_report(self, report: MissionCoherenceReport) -> None:
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "mission_coherence_guard_latest.json").write_text(
            json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8"
        )


def run_mission_coherence_guard(aiwg_root: str | Path = ".aiwg") -> MissionCoherenceReport:
    guard = MissionCoherenceGuard(aiwg_root=aiwg_root)
    report = guard.check_mission_coherence()
    guard.write_report(report)
    return report
