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
from layers.l2_brain.repo_intelligence_runtime import run_repo_intelligence_scan
from layers.l2_brain.folder_dossier_generator import generate_folder_dossiers
from layers.l2_brain.file_dossier_generator import generate_file_dossiers
from layers.l2_brain.technical_debt_intelligence import run_technical_debt_intelligence
from layers.l2_brain.plan_v1_completion_review import run_plan_v1_completion_review
from layers.l2_brain.context_enforcement_gate import run_context_enforcement_gate
from layers.l2_brain.repo_intelligence_query import query_repo_intelligence
from layers.l2_brain.operationalization_review import run_operationalization_review
from layers.l2_brain.metacognitive_quality_gate import run_metacognitive_quality_gate
from layers.l2_brain.spec_frontmatter_repair import repair_frontmatter
from layers.l2_brain.readiness_score_calibrator import run_readiness_score_calibration
from layers.l2_brain.memory_spine_entrypoint import retrieve_memory_for_intent
from layers.l2_brain.token_economy_benchmark import run_token_economy_benchmark
from layers.l2_brain.entrypoint_enforcement_auditor import run_entrypoint_enforcement_audit
from layers.l2_brain.metacognitive_loop_runtime import run_metacognitive_loop
from layers.l2_brain.mental_model_runtime import build_mental_model_for_intent
from layers.l2_brain.semantic_ontology_mapper import map_semantic_ontology
from layers.l2_brain.cognitive_frame_builder import build_cognitive_frame


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
            "repo-intelligence": self._cmd_repo_intelligence,
            "folder-dossiers": self._cmd_folder_dossiers,
            "file-dossiers": self._cmd_file_dossiers,
            "technical-debt": self._cmd_technical_debt,
            "completion-review": self._cmd_completion_review,
            "capability-scorecard": lambda: self._read_latest("plan_v1_runtime_capability_scorecard.json"),
            "integration-backlog": lambda: self._read_latest("integration_backlog.json"),
            "context-gate": self._cmd_context_gate,
            "repo-query": self._cmd_repo_query,
            "operationalization-review": self._cmd_operationalization_review,
            "repair-frontmatter": self._cmd_repair_frontmatter,
            "readiness-calibration": self._cmd_readiness_calibration,
            "memory-spine": self._cmd_memory_spine,
            "entrypoint-audit": self._cmd_entrypoint_audit,
            "token-benchmark": self._cmd_token_benchmark,
            "mental-model": self._cmd_mental_model,
            "ontology-map": self._cmd_ontology_map,
            "cognitive-frame": self._cmd_cognitive_frame,
            "metacognitive-loop": self._cmd_metacognitive_loop,
            "metacognitive-quality": self._cmd_metacognitive_quality,
            "epistemic-state": self._cmd_epistemic_state,
            "dialectical-review": self._cmd_dialectical_review,
            "philosophical-ontology": self._cmd_philosophical_ontology,
            "bias-report": self._cmd_bias_report,
            "metacognitive-flywheel": self._cmd_metacognitive_flywheel,
            # Pack 5.2.2
            "model-hygiene": self._cmd_model_hygiene,
            "quarantined-models": self._cmd_quarantined_models,
            "apply-evolution-delta": self._cmd_apply_evolution_delta,
            "self-improvement": self._cmd_self_improvement,
            "self-improvement-queue": self._cmd_self_improvement_queue,
            # Heartbeat-0
            "heartbeat": self._cmd_heartbeat,
            "heartbeat-dry-run": self._cmd_heartbeat_dry_run,
            "heartbeat-seed": self._cmd_heartbeat_seed,
            "heartbeat-status": self._cmd_heartbeat_status,
            "heartbeat-ledger": self._cmd_heartbeat_ledger,
            "whole-body-scan": self._cmd_whole_body_scan,
            "scan-calibration": self._cmd_scan_calibration,
            "wiring-matrix": self._cmd_wiring_matrix,
            "shadow-runtime": self._cmd_shadow_runtime,
            "systemic-coherence": self._cmd_systemic_coherence,
            # Heartbeat-2
            "6d-context": self._cmd_six_d_context,
            "context-optimize": self._cmd_context_optimize,
            "embedding-router": self._cmd_embedding_router,
            "4dtes-preflight": self._cmd_four_dtes_preflight,
            "daemon-gateway-bridge": self._cmd_daemon_gateway_bridge,
            "polyglot-probe": self._cmd_polyglot_probe,
            "context-circulation": self._cmd_context_circulation,
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

    def _cmd_repo_intelligence(self) -> CliCommandResult:
        res = run_repo_intelligence_scan(repo_root=self.aiwg_root.parent, aiwg_root=self.aiwg_root.name)
        return CliCommandResult(
            command="repo-intelligence",
            decision=res.decision,
            payload=res.to_dict(),
            evidence_refs=[".aiwg/reports/repo_intelligence_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_folder_dossiers(self) -> CliCommandResult:
        res = generate_folder_dossiers(aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="folder-dossiers",
            decision=res.decision,
            payload=res.to_dict(),
            evidence_refs=[".aiwg/reports/folder_dossier_index.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_file_dossiers(self) -> CliCommandResult:
        res = generate_file_dossiers(repo_root=self.aiwg_root.parent, aiwg_root=self.aiwg_root.name)
        return CliCommandResult(
            command="file-dossiers",
            decision=res.decision,
            payload=res.to_dict(),
            evidence_refs=[".aiwg/reports/file_dossier_index.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_technical_debt(self) -> CliCommandResult:
        res = run_technical_debt_intelligence(aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="technical-debt",
            decision=res.decision,
            payload=res.to_dict(),
            evidence_refs=[".aiwg/reports/technical_debt_intelligence_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_completion_review(self) -> CliCommandResult:
        res = run_plan_v1_completion_review(aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="completion-review",
            decision=res.decision,
            payload=res.to_dict(),
            evidence_refs=[".aiwg/reports/plan_v1_completion_review.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_context_gate(self) -> CliCommandResult:
        res = run_context_enforcement_gate({}, aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="context-gate",
            decision="PASS",
            payload=res.to_dict(),
            evidence_refs=[".aiwg/reports/context_enforcement_gate_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_repo_query(self) -> CliCommandResult:
        res = query_repo_intelligence({}, aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="repo-query",
            decision=res.decision,
            payload=res.to_dict(),
            evidence_refs=[".aiwg/reports/repo_intelligence_query_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_operationalization_review(self) -> CliCommandResult:
        res = run_operationalization_review(aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="operationalization-review",
            decision=res["decision"],
            payload=res,
            evidence_refs=[".aiwg/reports/operationalization_review_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_repair_frontmatter(self) -> CliCommandResult:
        res = repair_frontmatter()
        return CliCommandResult(
            command="repair-frontmatter",
            decision=res["decision"],
            payload=res,
            evidence_refs=[".aiwg/reports/spec_frontmatter_repair_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_readiness_calibration(self) -> CliCommandResult:
        res = run_readiness_score_calibration()
        return CliCommandResult(
            command="readiness-calibration",
            decision=res.decision,
            payload=res.to_dict(),
            warnings=[f.id for f in res.findings],
            evidence_refs=[".aiwg/reports/readiness_score_calibration_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_memory_spine(self) -> CliCommandResult:
        res = retrieve_memory_for_intent("status", aiwg_root=self.aiwg_root)
        return CliCommandResult(
            command="memory-spine",
            decision=res.decision,
            payload=res.to_dict(),
            warnings=res.warnings,
            evidence_refs=[".aiwg/reports/memory_spine_entrypoint_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_entrypoint_audit(self) -> CliCommandResult:
        res = run_entrypoint_enforcement_audit()
        return CliCommandResult(
            command="entrypoint-audit",
            decision=res.get("decision", "PASS"),
            payload=res,
            warnings=[a["entrypoint"] for a in res.get("audits", []) if not a.get("uses_memory_spine")],
            evidence_refs=[".aiwg/reports/entrypoint_enforcement_audit_latest.json"],
            generated_at=self._utc_now(),
        )

    def _cmd_mental_model(self) -> CliCommandResult:
        intent = "show current project mental model"
        model = build_mental_model_for_intent(intent, "analysis")
        return CliCommandResult("mental-model", "PASS", model.to_dict(), [], [".aiwg/reports/mental_model_runtime_latest.json"], model.created_at)

    def _cmd_ontology_map(self) -> CliCommandResult:
        intent = "show current project ontology"
        res = map_semantic_ontology(intent)
        return CliCommandResult("ontology-map", res["decision"], res, [], [".aiwg/reports/semantic_ontology_map_latest.json"], res["timestamp"])

    def _cmd_cognitive_frame(self) -> CliCommandResult:
        intent = "show current cognitive frame"
        model = build_mental_model_for_intent(intent, "analysis")
        frame = build_cognitive_frame(intent, model)
        return CliCommandResult("cognitive-frame", "PASS", frame.to_dict(), [], [".aiwg/reports/cognitive_frame_latest.json"], frame.created_at)

    def _cmd_metacognitive_loop(self) -> CliCommandResult:
        intent = "what should I do next?"
        res = run_metacognitive_loop(intent, aiwg_root=self.aiwg_root)
        return CliCommandResult("metacognitive-loop", res["decision"], res, res.get("warnings", []), [".aiwg/reports/metacognitive_loop_latest.json"], self._utc_now())

    def _cmd_metacognitive_quality(self) -> CliCommandResult:
        intent = "show current quality gate status"
        # Need to run a loop or mock one to get quality result
        res = run_metacognitive_loop(intent, aiwg_root=self.aiwg_root)
        quality = res.get("quality_gate", {})
        return CliCommandResult("metacognitive-quality", quality.get("decision", "FAIL"), quality, quality.get("warnings", []), [".aiwg/reports/metacognitive_quality_gate_latest.json"], self._utc_now())

    def _cmd_epistemic_state(self) -> CliCommandResult:
        res = run_metacognitive_loop("what do I know?", aiwg_root=self.aiwg_root)
        ep = res.get("epistemic_state", {})
        return CliCommandResult("epistemic-state", ep.get("decision", "FAIL"), ep, ep.get("warnings", []), [".aiwg/reports/epistemic_state_latest.json"], self._utc_now())

    def _cmd_dialectical_review(self) -> CliCommandResult:
        res = run_metacognitive_loop("challenge my current state", aiwg_root=self.aiwg_root)
        dial = res.get("dialectical_review", {})
        return CliCommandResult("dialectical-review", "PASS", dial, [], [".aiwg/reports/dialectical_review_latest.json"], self._utc_now())

    def _cmd_philosophical_ontology(self) -> CliCommandResult:
        res = run_metacognitive_loop("map my being", aiwg_root=self.aiwg_root)
        onto = res.get("philosophical_ontology", {})
        return CliCommandResult("philosophical-ontology", "PASS", onto, [], [".aiwg/reports/philosophical_ontology_latest.json"], self._utc_now())

    def _cmd_bias_report(self) -> CliCommandResult:
        res = run_metacognitive_loop("check my biases", aiwg_root=self.aiwg_root)
        bias = res.get("bias_report", {})
        return CliCommandResult("bias-report", bias.get("decision", "FAIL"), bias, [], [".aiwg/reports/cognitive_bias_report_latest.json"], self._utc_now())

    def _cmd_metacognitive_flywheel(self) -> CliCommandResult:
        res = run_metacognitive_loop("evolve my thought", aiwg_root=self.aiwg_root)
        delta = res.get("evolution_delta", {})
        return CliCommandResult("metacognitive-flywheel", "PASS", delta, [], [".aiwg/reports/metacognitive_evolution_delta_latest.json"], self._utc_now())


    # --- Pack 5.2.2 commands ------------------------------------------------

    def _cmd_model_hygiene(self) -> CliCommandResult:
        from layers.l2_brain.mental_model_truth_hygiene import run_mental_model_truth_hygiene
        res = run_mental_model_truth_hygiene(aiwg_root=self.aiwg_root)
        return CliCommandResult("model-hygiene", res.get("decision", "PASS"), res,
                                 evidence_refs=[".aiwg/reports/mental_model_truth_hygiene_latest.json"],
                                 generated_at=self._utc_now())

    def _cmd_quarantined_models(self) -> CliCommandResult:
        path = self.aiwg_root / "mental_models" / "runtime_model_quarantine.json"
        data = self._load_json(path)
        if isinstance(data, list):
            payload = {"quarantined": data, "count": len(data)}
        else:
            payload = data or {"quarantined": [], "count": 0}
        return CliCommandResult("quarantined-models", "PASS", payload,
                                 evidence_refs=[".aiwg/mental_models/runtime_model_quarantine.json"],
                                 generated_at=self._utc_now())

    def _cmd_apply_evolution_delta(self) -> CliCommandResult:
        from layers.l2_brain.evolution_delta_applier import apply_evolution_delta
        res = apply_evolution_delta(aiwg_root=self.aiwg_root)
        return CliCommandResult("apply-evolution-delta", res.get("decision", "PASS"), res,
                                 evidence_refs=[".aiwg/reports/evolution_delta_application_latest.json"],
                                 generated_at=self._utc_now())

    def _cmd_self_improvement(self) -> CliCommandResult:
        from layers.l2_brain.self_improvement_runtime import run_self_improvement_cycle
        res = run_self_improvement_cycle(aiwg_root=self.aiwg_root)
        return CliCommandResult("self-improvement", res.get("decision", "PASS"), res,
                                 warnings=res.get("warnings", []),
                                 evidence_refs=[".aiwg/reports/self_improvement_cycle_latest.json"],
                                 generated_at=self._utc_now())

    def _cmd_self_improvement_queue(self) -> CliCommandResult:
        data = self._load_json(self.aiwg_root / "reports" / "self_improvement_action_queue.json")
        return CliCommandResult("self-improvement-queue", "PASS", data or {"actions": []},
                                 evidence_refs=[".aiwg/reports/self_improvement_action_queue.json"],
                                 generated_at=self._utc_now())

    # --- Heartbeat-0 commands -----------------------------------------------

    def _cmd_heartbeat(self) -> CliCommandResult:
        from layers.l2_brain.heartbeat_lifecycle_runtime import run_heartbeat
        res = run_heartbeat(mode="observe_only", aiwg_root=self.aiwg_root)
        return CliCommandResult("heartbeat", res.get("decision", "PASS"), res,
                                 warnings=res.get("warnings", []),
                                 evidence_refs=[".aiwg/reports/heartbeat_latest.json"],
                                 generated_at=self._utc_now())

    def _cmd_heartbeat_dry_run(self) -> CliCommandResult:
        from layers.l2_brain.heartbeat_scheduler import HeartbeatScheduler
        scheduler = HeartbeatScheduler(aiwg_root=self.aiwg_root)
        res = scheduler.dry_run()
        return CliCommandResult("heartbeat-dry-run", res.get("decision", "PASS"), res,
                                 evidence_refs=[".aiwg/reports/heartbeat_scheduler_latest.json"],
                                 generated_at=self._utc_now())

    def _cmd_heartbeat_seed(self) -> CliCommandResult:
        from layers.l2_brain.heartbeat_scheduler import HeartbeatScheduler
        scheduler = HeartbeatScheduler(aiwg_root=self.aiwg_root)
        res = scheduler.load_next_seed()
        return CliCommandResult("heartbeat-seed", "PASS", res,
                                 evidence_refs=[".aiwg/heartbeat/next_heartbeat_seed.json"],
                                 generated_at=self._utc_now())

    def _cmd_heartbeat_status(self) -> CliCommandResult:
        path = self.aiwg_root / "heartbeat" / "latest_heartbeat.json"
        data = self._load_json(path)
        return CliCommandResult("heartbeat-status", "PASS", data or {},
                                 evidence_refs=[".aiwg/heartbeat/latest_heartbeat.json"],
                                 generated_at=self._utc_now())

    def _cmd_heartbeat_ledger(self) -> CliCommandResult:
        path = self.aiwg_root / "heartbeat" / "heartbeat_ledger.jsonl"
        count = 0
        if path.exists():
            try:
                count = sum(1 for _ in path.open("r", encoding="utf-8"))
            except Exception:
                pass
        return CliCommandResult("heartbeat-ledger", "PASS", {"count": count},
                                 evidence_refs=[".aiwg/heartbeat/heartbeat_ledger.jsonl"],
                                 generated_at=self._utc_now())

    def _cmd_whole_body_scan(self) -> CliCommandResult:
        from whole_body_scanner import WholeBodyScanner
        scanner = WholeBodyScanner()
        res = scanner.run_scan()
        return CliCommandResult("whole-body-scan", "PASS", res,
                                 evidence_refs=[
                                     ".aiwg/reports/whole_body_scan_latest.json",
                                     ".aiwg/reports/whole_body_scan_latest.md"
                                 ],
                                 generated_at=self._utc_now())

    def _cmd_six_d_context(self) -> CliCommandResult:
        from six_dimensional_context_runtime import build_6d_context_packet
        res = build_6d_context_packet(intent="repair kuzu", aiwg_root=self.aiwg_root.parent)
        return CliCommandResult("6d-context", res.get("decision", "PASS"), res,
                                 evidence_refs=[
                                     ".aiwg/reports/6d_context_packet_latest.json",
                                     ".aiwg/reports/6d_context_packet_latest.md"
                                 ],
                                 generated_at=self._utc_now())

    def _cmd_context_optimize(self) -> CliCommandResult:
        from six_dimensional_context_runtime import build_6d_context_packet
        from context_packet_optimizer import optimize_context_packet
        packet = build_6d_context_packet(intent="repair kuzu", aiwg_root=self.aiwg_root.parent)
        res = optimize_context_packet(packet=packet, aiwg_root=self.aiwg_root.parent)
        return CliCommandResult("context-optimize", res.get("decision", "PASS"), res,
                                 evidence_refs=[
                                     ".aiwg/reports/context_packet_optimization_latest.json",
                                     ".aiwg/reports/context_packet_optimization_latest.md"
                                 ],
                                 generated_at=self._utc_now())

    def _cmd_embedding_router(self) -> CliCommandResult:
        from embedding_memory_router import run_embedding_memory_router_demo
        res = run_embedding_memory_router_demo(intent="repair kuzu", aiwg_root=self.aiwg_root.parent)
        return CliCommandResult("embedding-router", res.get("decision", "PASS"), res,
                                 evidence_refs=[
                                     ".aiwg/reports/embedding_memory_router_latest.json",
                                     ".aiwg/reports/embedding_memory_router_latest.md"
                                 ],
                                 generated_at=self._utc_now())

    def _cmd_four_dtes_preflight(self) -> CliCommandResult:
        from four_dtes_persistence_preflight import run_4dtes_preflight
        res = run_4dtes_preflight(aiwg_root=self.aiwg_root.parent)
        return CliCommandResult("4dtes-preflight", res.get("decision", "PASS"), res,
                                 evidence_refs=[
                                     ".aiwg/reports/4dtes_persistence_preflight_latest.json",
                                     ".aiwg/reports/4dtes_persistence_preflight_latest.md"
                                 ],
                                 generated_at=self._utc_now())

    def _cmd_daemon_gateway_bridge(self) -> CliCommandResult:
        from daemon_gateway_heartbeat_bridge import run_daemon_gateway_bridge_demo
        res = run_daemon_gateway_bridge_demo(intent="repair kuzu", aiwg_root=self.aiwg_root.parent)
        return CliCommandResult("daemon-gateway-bridge", res.get("decision", "PASS"), res,
                                 evidence_refs=[
                                     ".aiwg/reports/daemon_gateway_heartbeat_bridge_latest.json",
                                     ".aiwg/reports/daemon_gateway_heartbeat_bridge_latest.md"
                                 ],
                                 generated_at=self._utc_now())

    def _cmd_polyglot_probe(self) -> CliCommandResult:
        from polyglot_probe_orchestrator import run_polyglot_probe
        res = run_polyglot_probe(aiwg_root=self.aiwg_root.parent)
        return CliCommandResult("polyglot-probe", res.get("decision", "PASS"), res,
                                 evidence_refs=[
                                     ".aiwg/reports/polyglot_probe_latest.json",
                                     ".aiwg/reports/polyglot_probe_latest.md"
                                 ],
                                 generated_at=self._utc_now())

    def _cmd_context_circulation(self) -> CliCommandResult:
        from context_circulation_runtime import run_cognitive_circulation
        res = run_cognitive_circulation(intent="repair kuzu", aiwg_root=self.aiwg_root.parent)
        return CliCommandResult("context-circulation", "PASS", res,
                                 evidence_refs=[
                                     ".aiwg/reports/6d_context_packet_latest.json",
                                     ".aiwg/reports/context_packet_optimization_latest.json",
                                     ".aiwg/reports/embedding_memory_router_latest.json",
                                     ".aiwg/reports/4dtes_persistence_preflight_latest.json",
                                     ".aiwg/reports/daemon_gateway_heartbeat_bridge_latest.json",
                                     ".aiwg/reports/polyglot_probe_latest.json"
                                 ],
                                 generated_at=self._utc_now())


    def _cmd_token_benchmark(self) -> CliCommandResult:
        res = run_token_economy_benchmark()
        return CliCommandResult(
            command="token-benchmark",
            decision=res.decision,
            payload=res.to_dict(),
            evidence_refs=[".aiwg/reports/token_economy_benchmark_latest.json"],
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
