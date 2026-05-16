from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Allow direct script execution: `python3 layers/l2_brain/cli_control_plane.py ...`
if __package__ in {None, ""}:
    _ROOT = Path(__file__).resolve().parents[2]
    if str(_ROOT) not in sys.path:
        sys.path.append(str(_ROOT))
    _L2 = _ROOT / "layers" / "l2_brain"
    if str(_L2) not in sys.path:
        sys.path.append(str(_L2))

from layers.l2_brain.local_context_compressor import LocalContextCompressor
from layers.l2_brain.tui_process_monitor import TuiProcessMonitor
from layers.l6_skin.dashboard_renderer import DashboardRenderer


@dataclass
class CliCommandResult:
    command: str
    decision: str  # PASS|PASS_WITH_WARNINGS|FAIL
    payload: dict[str, Any]
    warnings: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CliControlPlane:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"

    def run_command(self, command: str) -> CliCommandResult:
        command = command.strip()
        handlers = {
            "status": self._cmd_status,
            "health": self._cmd_health,
            "latest-context": lambda: self._read_latest("context_package_latest.json"),
            "latest-frame": lambda: self._read_latest("prompt_frame_latest.json"),
            "cache-summary": lambda: self._read_latest("prompt_cache_summary_latest.json"),
            "restart-gate": lambda: self._read_latest("restart_integration_gate_latest.json"),
            "benchmark": lambda: self._read_latest("context_efficiency_benchmark_latest.json"),
            "flywheel": lambda: self._read_latest("evolution_flywheel_latest.json"),
            "next-action": self._cmd_next_action,
            "compress-context": self._cmd_compress_context,
            "dashboard-data": self._cmd_dashboard_data,
        }

        if command not in handlers:
            result = CliCommandResult(
                command=command,
                decision="FAIL",
                payload={"error": "unknown_command", "available_commands": sorted(handlers)},
                warnings=["unknown_command"],
                evidence_refs=[],
                generated_at=self._utc_now(),
            )
            self._write_latest(result)
            return result

        try:
            result = handlers[command]()
        except Exception as exc:
            result = CliCommandResult(
                command=command,
                decision="FAIL",
                payload={"error": str(exc)},
                warnings=["command_execution_failed"],
                evidence_refs=[],
                generated_at=self._utc_now(),
            )

        self._write_latest(result)
        return result

    def _cmd_status(self) -> CliCommandResult:
        monitor = TuiProcessMonitor(aiwg_root=self.aiwg_root)
        snapshot = monitor.build_process_monitor_snapshot(write_output=True)
        payload = snapshot.to_dict()
        return CliCommandResult(
            command="status",
            decision=snapshot.decision,
            payload=payload,
            warnings=snapshot.warnings,
            evidence_refs=snapshot.evidence_refs,
            generated_at=self._utc_now(),
        )

    def _cmd_health(self) -> CliCommandResult:
        required = [
            self.aiwg_root / "evolution" / "current_position.json",
            self.aiwg_root / "evolution" / "next_phase_seed.json",
            self.reports_root / "context_quant_result_latest.json",
            self.reports_root / "prompt_frame_latest.json",
            self.reports_root / "evolution_flywheel_latest.json",
        ]
        missing = [p.as_posix() for p in required if not p.exists()]
        decision = "PASS" if not missing else "PASS_WITH_WARNINGS"
        return CliCommandResult(
            command="health",
            decision=decision,
            payload={"missing": missing, "required_count": len(required)},
            warnings=["missing_required_runtime_artifact"] if missing else [],
            evidence_refs=[p.as_posix() for p in required],
            generated_at=self._utc_now(),
        )

    def _cmd_next_action(self) -> CliCommandResult:
        flywheel = self._load_json(self.reports_root / "evolution_flywheel_latest.json")
        next_seed = self._load_json(self.aiwg_root / "evolution" / "next_phase_seed.json")

        action = flywheel.get("decision", "review_runtime_outputs")
        recommended_phase = flywheel.get("recommended_next_phase", next_seed.get("next_phase", "unknown"))
        payload = {
            "decision": action,
            "recommended_next_phase": recommended_phase,
            "why": flywheel.get("why_this_is_the_next_lever", "no_reason_available"),
        }
        warnings = [] if flywheel else ["missing_flywheel_latest"]
        decision = "PASS" if flywheel else "PASS_WITH_WARNINGS"
        return CliCommandResult(
            command="next-action",
            decision=decision,
            payload=payload,
            warnings=warnings,
            evidence_refs=[".aiwg/reports/evolution_flywheel_latest.json", ".aiwg/evolution/next_phase_seed.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_compress_context(self) -> CliCommandResult:
        compressor = LocalContextCompressor(aiwg_root=self.aiwg_root)
        payload = compressor.compress_latest_context(write_output=True)
        warnings = list(payload.get("warnings", []))
        decision = "PASS" if bool(payload.get("required_preserved", True)) else "FAIL"
        if warnings and decision == "PASS":
            decision = "PASS_WITH_WARNINGS"
        return CliCommandResult(
            command="compress-context",
            decision=decision,
            payload=payload,
            warnings=warnings,
            evidence_refs=[".aiwg/reports/local_context_compression_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_dashboard_data(self) -> CliCommandResult:
        renderer = DashboardRenderer(aiwg_root=self.aiwg_root)
        state = renderer.build_dashboard_state()
        renderer.write_dashboard_outputs(state)
        decision = "PASS" if not state.warnings else "PASS_WITH_WARNINGS"
        return CliCommandResult(
            command="dashboard-data",
            decision=decision,
            payload=state.to_dict(),
            warnings=state.warnings,
            evidence_refs=[
                ".aiwg/reports/dashboard_l6_latest.json",
                ".aiwg/reports/dashboard_l6_latest.html",
            ],
            generated_at=self._utc_now(),
        )

    def _read_latest(self, filename: str) -> CliCommandResult:
        path = self.reports_root / filename
        if not path.exists():
            return CliCommandResult(
                command=filename.replace("_latest.json", ""),
                decision="PASS_WITH_WARNINGS",
                payload={},
                warnings=[f"missing:{filename}"],
                evidence_refs=[path.as_posix()],
                generated_at=self._utc_now(),
            )
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return CliCommandResult(
                command=filename.replace("_latest.json", ""),
                decision="PASS",
                payload=payload,
                warnings=[],
                evidence_refs=[path.as_posix()],
                generated_at=self._utc_now(),
            )
        except Exception:
            return CliCommandResult(
                command=filename.replace("_latest.json", ""),
                decision="FAIL",
                payload={},
                warnings=[f"invalid_json:{filename}"],
                evidence_refs=[path.as_posix()],
                generated_at=self._utc_now(),
            )

    def _write_latest(self, result: CliCommandResult) -> None:
        self.reports_root.mkdir(parents=True, exist_ok=True)
        out = self.reports_root / "cli_control_plane_latest.json"
        out.write_text(json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8")

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_cli_command(argv: list[str] | None = None) -> CliCommandResult:
    args = argv if argv is not None else sys.argv[1:]
    command = args[0] if args else "status"
    plane = CliControlPlane(aiwg_root=".aiwg")
    return plane.run_command(command)


def main(argv: list[str] | None = None) -> int:
    result = run_cli_command(argv)
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.decision in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
