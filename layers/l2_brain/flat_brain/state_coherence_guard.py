from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class StateCoherenceFinding:
    artifact: str
    message: str
    expected: Any
    actual: Any
    severity: str  # ERROR|WARNING


@dataclass
class StateCoherenceReport:
    decision: str  # PASS|PASS_WITH_WARNINGS|FAIL
    findings: list[StateCoherenceFinding] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "findings": [asdict(f) for f in self.findings],
            "generated_at": self.generated_at,
        }


class StateCoherenceGuard:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"
        self.evolution_root = self.aiwg_root / "evolution"

    def check_state_coherence(self) -> StateCoherenceReport:
        findings: list[StateCoherenceFinding] = []

        current_pos = self._load_json(self.evolution_root / "current_position.json")
        next_seed = self._load_json(self.evolution_root / "next_phase_seed.json")

        if not current_pos:
            findings.append(StateCoherenceFinding("current_position.json", "missing or invalid", "json_object", "none", "ERROR"))
        if not next_seed:
            findings.append(StateCoherenceFinding("next_phase_seed.json", "missing or invalid", "json_object", "none", "ERROR"))

        expected_current = str(current_pos.get("current_phase", "unknown"))
        expected_next = str(next_seed.get("next_phase", "unknown"))

        # Check latest reports
        artifacts = {
            "cli_control_plane_latest.json": self.reports_root / "cli_control_plane_latest.json",
            "process_monitor_latest.json": self.reports_root / "process_monitor_latest.json",
            "dashboard_l6_latest.json": self.reports_root / "dashboard_l6_latest.json",
        }

        for name, path in artifacts.items():
            if not path.exists():
                findings.append(StateCoherenceFinding(name, "missing", "present", "missing", "WARNING"))
                continue

            data = self._load_json(path)
            if not data:
                findings.append(StateCoherenceFinding(name, "invalid json", "json_object", "none", "ERROR"))
                continue

            # Flatten payload for CLI result
            if name == "cli_control_plane_latest.json":
                payload = data.get("payload", {})
                # cli status payload is a monitor snapshot
                if data.get("command") == "status":
                    actual_current = str(payload.get("current_phase", "unknown"))
                    actual_next = str(payload.get("next_phase", "unknown"))
                else:
                    # just skip checking phases if it wasn't a status command, 
                    # OR check if it has phases at all
                    actual_current = expected_current
                    actual_next = expected_next
            else:
                actual_current = str(data.get("current_phase", "unknown"))
                actual_next = str(data.get("next_phase", "unknown"))

            if actual_current != expected_current:
                findings.append(StateCoherenceFinding(name, "current_phase mismatch", expected_current, actual_current, "ERROR"))
            if actual_next != expected_next:
                findings.append(StateCoherenceFinding(name, "next_phase mismatch", expected_next, actual_next, "ERROR"))

        # Check Dashboard HTML
        html_path = self.reports_root / "dashboard_l6_latest.html"
        if html_path.exists():
            html_content = html_path.read_text(encoding="utf-8")
            if f"<div class=\"v\">{expected_current}</div>" not in html_content:
                findings.append(StateCoherenceFinding("dashboard_l6_latest.html", "current_phase mismatch in HTML", expected_current, "mismatch", "ERROR"))
            if f"<div class=\"v\">{expected_next}</div>" not in html_content:
                findings.append(StateCoherenceFinding("dashboard_l6_latest.html", "next_phase mismatch in HTML", expected_next, "mismatch", "ERROR"))
        else:
            findings.append(StateCoherenceFinding("dashboard_l6_latest.html", "missing", "present", "missing", "WARNING"))

        # Decision
        errors = [f for f in findings if f.severity == "ERROR"]
        warnings = [f for f in findings if f.severity == "WARNING"]

        if errors:
            decision = "FAIL"
        elif warnings:
            decision = "PASS_WITH_WARNINGS"
        else:
            decision = "PASS"

        return StateCoherenceReport(
            decision=decision,
            findings=findings,
            generated_at=self._utc_now(),
        )

    def write_report(self, report: StateCoherenceReport) -> None:
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "state_coherence_guard_latest.json").write_text(
            json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8"
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


def run_state_coherence_guard(aiwg_root: str | Path = ".aiwg") -> StateCoherenceReport:
    guard = StateCoherenceGuard(aiwg_root=aiwg_root)
    report = guard.check_state_coherence()
    guard.write_report(report)
    return report
