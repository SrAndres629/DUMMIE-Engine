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
from layers.l2_brain.mission_coherence_guard import run_mission_coherence_guard
from layers.l2_brain.mission_orchestrator_dag import build_dag_from_mission_plan
from layers.l2_brain.mission_planner import create_mission_plan
from layers.l2_brain.repo_probe_runner import run_repo_probe
from layers.l2_brain.state_coherence_guard import run_state_coherence_guard
from layers.l2_brain.strategic_partner_swarm import run_strategic_partner_swarm
from layers.l2_brain.tui_process_monitor import TuiProcessMonitor
from layers.l6_skin.dashboard_renderer import DashboardRenderer
from layers.l2_brain.debate_review_runtime import run_debate_review
from layers.l2_brain.mission_autonomy_contract import run_mission_autonomy_contract
from layers.l2_brain.trusted_workstation_mode import run_trusted_workstation_mode
from layers.l2_brain.chaos_regression_testing import run_chaos_regression_tests
from layers.l2_brain.autonomous_strategic_partner_runtime import run_autonomous_strategic_partner_runtime


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
            "state-coherence": self._cmd_state_coherence,
            "repo-probe": self._cmd_repo_probe,
            "mission-plan": self._cmd_mission_plan,
            "mission-dag": self._cmd_mission_dag,
            "next-node": self._cmd_next_node,
            "mission-coherence": self._cmd_mission_coherence,
            "strategic-swarm": self._cmd_strategic_swarm,
            "swarm": self._cmd_strategic_swarm,
            "debate-review": self._cmd_debate_review,
            "debate": self._cmd_debate_review,
            "autonomy-contract": self._cmd_autonomy_contract,
            "autonomy": self._cmd_autonomy_contract,
            "trusted-workstation": self._cmd_trusted_workstation,
            "workstation": self._cmd_trusted_workstation,
            "chaos-regression": self._cmd_chaos_regression,
            "chaos": self._cmd_chaos_regression,
            "autonomous-runtime": self._cmd_autonomous_runtime,
            "autonomous": self._cmd_autonomous_runtime,
            "plan-v1-status": self._cmd_plan_v1_status,
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

    def _cmd_state_coherence(self) -> CliCommandResult:
        report = run_state_coherence_guard(aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="state-coherence",
            decision=report.decision,
            payload=report.to_dict(),
            warnings=[f.message for f in report.findings if f.severity == "WARNING"],
            evidence_refs=[".aiwg/reports/state_coherence_guard_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_repo_probe(self) -> CliCommandResult:
        result = run_repo_probe(root=self.aiwg_root.parent)
        return CliCommandResult(
            command="repo-probe",
            decision=result.decision,
            payload=result.to_dict(),
            warnings=[f.message for f in result.findings if f.severity == "WARNING"],
            evidence_refs=[".aiwg/reports/repo_probe_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_mission_plan(self) -> CliCommandResult:
        plan = create_mission_plan(root=self.aiwg_root.parent)
        return CliCommandResult(
            command="mission-plan",
            decision=plan.decision,
            payload=plan.to_dict(),
            warnings=plan.risk_register,
            evidence_refs=[
                ".aiwg/reports/mission_plan_latest.json",
                ".aiwg/reports/mission_plan_latest.md",
            ],
            generated_at=self._utc_now(),
        )

    def _cmd_mission_dag(self) -> CliCommandResult:
        # We need a plan first
        plan_path = self.reports_root / "mission_plan_latest.json"
        if not plan_path.exists():
             self._cmd_mission_plan()
        
        try:
            with open(plan_path, "r") as f:
                plan_data = json.load(f)
            # Re-wrap in a simple object for the DAG builder
            class PlanMock: pass
            plan = PlanMock()
            plan.mission_id = plan_data["mission_id"]
            plan.l2_phases = [type("Phase", (), p) for p in plan_data["l2_phases"]]
            plan.l3_microphases = [type("MicroPhase", (), m) for m in plan_data["l3_microphases"]]
            
            dag = build_dag_from_mission_plan(plan, root=self.aiwg_root.parent)
            return CliCommandResult(
                command="mission-dag",
                decision=dag.decision,
                payload=dag.to_dict(),
                warnings=[],
                evidence_refs=[".aiwg/reports/mission_orchestrator_dag_latest.json"],
                generated_at=self._utc_now(),
            )
        except Exception as exc:
            return CliCommandResult(
                command="mission-dag",
                decision="FAIL",
                payload={"error": str(exc)},
                generated_at=self._utc_now(),
            )

    def _cmd_next_node(self) -> CliCommandResult:
        dag_path = self.reports_root / "mission_orchestrator_dag_latest.json"
        if not dag_path.exists():
            return CliCommandResult(
                command="next-node",
                decision="FAIL",
                payload={"error": "DAG missing. Run mission-dag first."},
                generated_at=self._utc_now(),
            )
        
        data = self._read_latest("next_executable_node_latest.json")
        return CliCommandResult(
            command="next-node",
            decision=data.decision,
            payload=data.payload,
            warnings=data.warnings,
            evidence_refs=data.evidence_refs,
            generated_at=self._utc_now(),
        )

    def _cmd_mission_coherence(self) -> CliCommandResult:
        report = run_mission_coherence_guard(aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="mission-coherence",
            decision=report.decision,
            payload=report.to_dict(),
            warnings=[f.message for f in report.findings if f.severity == "WARNING"],
            evidence_refs=[".aiwg/reports/mission_coherence_guard_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_strategic_swarm(self) -> CliCommandResult:
        decision = run_strategic_partner_swarm(aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="strategic-swarm",
            decision="PASS" if decision.decision == "continue_next_phase" else "PASS_WITH_WARNINGS" if "repair" in decision.decision else "FAIL",
            payload=decision.to_dict(),
            warnings=decision.blocking_reasons,
            evidence_refs=[".aiwg/reports/strategic_partner_swarm_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_debate_review(self) -> CliCommandResult:
        result = run_debate_review(aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="debate-review",
            decision="PASS" if result.decision in ["accept_plan", "accept_with_objections"] else "FAIL",
            payload=result.to_dict(),
            warnings=result.objections,
            evidence_refs=[".aiwg/reports/debate_review_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_autonomy_contract(self) -> CliCommandResult:
        result = run_mission_autonomy_contract(aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="autonomy-contract",
            decision=result.get("decision", "PASS"),
            payload=result,
            warnings=result.get("warnings", []),
            evidence_refs=[".aiwg/reports/mission_autonomy_contract_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_trusted_workstation(self) -> CliCommandResult:
        report = run_trusted_workstation_mode(aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="trusted-workstation",
            decision=report.get("decision", "PASS"),
            payload=report,
            warnings=report.get("warnings", []),
            evidence_refs=[".aiwg/reports/trusted_workstation_mode_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_chaos_regression(self) -> CliCommandResult:
        report = run_chaos_regression_tests(aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="chaos-regression",
            decision=report.decision,
            payload=report.to_dict(),
            warnings=report.warnings,
            evidence_refs=[".aiwg/reports/chaos_regression_report_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_autonomous_runtime(self) -> CliCommandResult:
        decision = run_autonomous_strategic_partner_runtime(aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="autonomous-runtime",
            decision="PASS" if decision.decision != "block_due_to_safety" else "FAIL",
            payload=decision.to_dict(),
            warnings=decision.blocking_reasons,
            evidence_refs=[".aiwg/reports/autonomous_strategic_partner_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_plan_v1_status(self) -> CliCommandResult:
        decision = run_autonomous_strategic_partner_runtime(aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="plan-v1-status",
            decision="PASS" if decision.plan_v1_completion_status == "complete" else "PASS_WITH_WARNINGS",
            payload={"status": decision.plan_v1_completion_status},
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
