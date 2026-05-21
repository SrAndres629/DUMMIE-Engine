import json
from pathlib import Path

from layers.l2_brain.mission.cli_control_plane import CliControlPlane
from layers.l2_brain.governance.tui_process_monitor import TuiProcessMonitor
from layers.l6_skin.dashboard_renderer import DashboardRenderer


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _seed(aiwg: Path) -> None:
    reports = aiwg / "reports"
    _write_json(aiwg / "evolution" / "current_position.json", {"plan": "DUMMIE", "current_phase": "P17", "next_required_phase": "P18"})
    _write_json(aiwg / "evolution" / "next_phase_seed.json", {"next_phase": "P18", "name": "CLI Control Plane"})
    _write_json(aiwg / "world_model" / "project_world_model.json", {"version": "1.0.0", "next_phase_requirements": {"next_phase": "P18"}})
    _write_json(reports / "spec_coverage_matrix.json", {"coverage_summary": {"spec_families_total": 100, "complete_triplets": 97}})
    _write_json(reports / "restart_integration_gate_latest.json", {"decision": "PASS"})
    _write_json(reports / "context_efficiency_benchmark_latest.json", {"decision": "IMPROVED"})
    _write_json(reports / "evolution_flywheel_latest.json", {"decision": "continue_next_phase", "recommended_next_phase": "P18"})
    _write_json(reports / "prompt_cache_summary_latest.json", {"cache_hit_ratio": 0.5})
    _write_json(reports / "stale_memory_report.json", {"findings": []})
    _write_json(reports / "context_quant_result_latest.json", {"kept_refs": ["state:current_position"], "dropped_refs": [], "compressed_refs": [], "estimated_total_tokens": 10})
    _write_json(reports / "context_package_latest.json", {"items": [{"ref": "state:current_position", "summary": "ok", "token_role": "summary_only", "truth_rank": 90, "freshness_status": "fresh", "required": True, "estimated_tokens": 10, "risk_flags": []}]})
    _write_json(reports / "context_receipt_latest.json", {"decision": "ALLOW", "budget_limit": 100})
    _write_json(reports / "prompt_frame_latest.json", {"prompt_sections": {"system": ["sys"]}, "frame_id": "f1"})
    _write_json(aiwg / "notes" / "folder_notes_manifest.json", {"folders": []})


def test_control_surface_integration_pipeline(tmp_path: Path):
    aiwg = tmp_path / ".aiwg"
    _seed(aiwg)

    cli = CliControlPlane(aiwg_root=aiwg)
    status = cli.run_command("status")
    assert status.decision in {"PASS", "PASS_WITH_WARNINGS"}

    comp = cli.run_command("compress-context")
    assert comp.decision in {"PASS", "PASS_WITH_WARNINGS"}

    mon = TuiProcessMonitor(aiwg_root=aiwg)
    snap = mon.build_process_monitor_snapshot(write_output=True)
    assert snap.current_phase == "P17"

    dash = DashboardRenderer(aiwg_root=aiwg)
    state = dash.build_dashboard_state()
    dash.write_dashboard_outputs(state)

    for rel in [
        "reports/cli_control_plane_latest.json",
        "reports/process_monitor_latest.json",
        "reports/dashboard_l6_latest.json",
        "reports/local_context_compression_latest.json",
    ]:
        p = aiwg / rel
        assert p.exists()
        json.loads(p.read_text(encoding="utf-8"))
