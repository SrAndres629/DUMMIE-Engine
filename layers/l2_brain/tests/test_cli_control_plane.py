import json
from pathlib import Path

from layers.l2_brain.mission.cli_control_plane import CliControlPlane


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _seed(aiwg: Path) -> None:
    reports = aiwg / "reports"
    _write_json(aiwg / "evolution" / "current_position.json", {"current_phase": "P17", "next_required_phase": "P18"})
    _write_json(aiwg / "evolution" / "next_phase_seed.json", {"next_phase": "P18", "name": "CLI Control Plane"})
    _write_json(aiwg / "world_model" / "project_world_model.json", {"version": "1.0.0", "next_phase_requirements": {"next_phase": "P18"}})
    _write_json(reports / "spec_coverage_matrix.json", {"coverage_summary": {"spec_families_total": 100, "complete_triplets": 97}})
    _write_json(reports / "restart_integration_gate_latest.json", {"decision": "PASS"})
    _write_json(reports / "context_efficiency_benchmark_latest.json", {"decision": "IMPROVED"})
    _write_json(reports / "evolution_flywheel_latest.json", {"decision": "continue_next_phase", "recommended_next_phase": "P18"})
    _write_json(reports / "prompt_cache_summary_latest.json", {"cache_hit_ratio": 0.5})
    _write_json(reports / "stale_memory_report.json", {"findings": []})
    _write_json(reports / "context_quant_result_latest.json", {"kept_refs": [], "dropped_refs": [], "compressed_refs": [], "estimated_total_tokens": 10})
    _write_json(reports / "context_package_latest.json", {"items": [{"ref": "x", "summary": "ok", "token_role": "summary_only", "truth_rank": 60, "freshness_status": "fresh", "required": True, "estimated_tokens": 10, "risk_flags": []}]})
    _write_json(reports / "context_receipt_latest.json", {"decision": "ALLOW", "budget_limit": 100})
    _write_json(reports / "prompt_frame_latest.json", {"prompt_sections": {"system": ["sys"]}, "frame_id": "f1"})
    _write_json(aiwg / "notes" / "folder_notes_manifest.json", {"folders": []})
    _write_json(aiwg / "mental_models" / "runtime_model_index.json", {})

    # Seed for heartbeat
    _write_json(reports / "self_improvement_action_queue.json", {
        "actions": [{"action_type": "increase_test_coverage", "priority": "high", "status": "proposed"}],
        "blocked": []
    })
    _write_json(reports / "readiness_score_calibration_latest.json", {"findings": []})
    _write_json(reports / "mental_model_truth_hygiene_latest.json", {})
    _write_json(reports / "evolution_delta_application_latest.json", {})
    _write_json(reports / "epistemic_state_latest.json", {})
    _write_json(reports / "cognitive_bias_report_latest.json", {})
    _write_json(reports / "memory_spine_entrypoint_latest.json", {})
    _write_json(reports / "metacognitive_loop_latest.json", {})


def test_cli_status_returns_json_result(tmp_path: Path):
    aiwg = tmp_path / ".aiwg"
    _seed(aiwg)
    cli = CliControlPlane(aiwg_root=aiwg)

    res = cli.run_command("status")
    assert res.decision in {"PASS", "PASS_WITH_WARNINGS"}
    assert isinstance(res.payload, dict)
    assert (aiwg / "reports" / "cli_control_plane_latest.json").exists()


def test_cli_flywheel_reads_latest_output(tmp_path: Path):
    aiwg = tmp_path / ".aiwg"
    _seed(aiwg)
    cli = CliControlPlane(aiwg_root=aiwg)

    res = cli.run_command("flywheel")
    assert res.decision == "PASS"
    assert res.payload.get("decision") == "continue_next_phase"


def test_cli_missing_latest_file_warns_not_crash(tmp_path: Path):
    aiwg = tmp_path / ".aiwg"
    _seed(aiwg)
    (aiwg / "reports" / "evolution_flywheel_latest.json").unlink()

    cli = CliControlPlane(aiwg_root=aiwg)
    res = cli.run_command("flywheel")
    assert res.decision == "PASS_WITH_WARNINGS"


def test_cli_compress_context_produces_output(tmp_path: Path):
    aiwg = tmp_path / ".aiwg"
    _seed(aiwg)
    cli = CliControlPlane(aiwg_root=aiwg)

    res = cli.run_command("compress-context")
    assert res.decision in {"PASS", "PASS_WITH_WARNINGS"}
    assert (aiwg / "reports" / "local_context_compression_latest.json").exists()


def test_cli_heartbeat(tmp_path: Path):
    aiwg = tmp_path / ".aiwg"
    _seed(aiwg)
    cli = CliControlPlane(aiwg_root=aiwg)

    res = cli.run_command("heartbeat")
    assert res.command == "heartbeat"
    assert res.decision in {"PASS", "PASS_WITH_WARNINGS", "NEEDS_HUMAN_REVIEW"}
    assert (aiwg / "reports" / "heartbeat_latest.json").exists()


def test_cli_heartbeat_dry_run(tmp_path: Path):
    aiwg = tmp_path / ".aiwg"
    _seed(aiwg)
    cli = CliControlPlane(aiwg_root=aiwg)

    res = cli.run_command("heartbeat-dry-run")
    assert res.command == "heartbeat-dry-run"
    assert res.decision in {"PASS", "PASS_WITH_WARNINGS"}
    assert (aiwg / "reports" / "heartbeat_scheduler_latest.json").exists()
