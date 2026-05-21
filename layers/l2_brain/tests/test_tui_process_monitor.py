import json
from pathlib import Path

from layers.l2_brain.governance.tui_process_monitor import TuiProcessMonitor


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_tui_process_monitor_build_and_render(tmp_path: Path):
    aiwg = tmp_path / ".aiwg"
    reports = aiwg / "reports"

    _write_json(aiwg / "evolution" / "current_position.json", {"current_phase": "P17"})
    _write_json(aiwg / "evolution" / "next_phase_seed.json", {"next_phase": "P18"})
    _write_json(reports / "restart_integration_gate_latest.json", {"decision": "PASS"})
    _write_json(reports / "context_efficiency_benchmark_latest.json", {"decision": "IMPROVED"})
    _write_json(reports / "evolution_flywheel_latest.json", {"decision": "continue_next_phase", "blocking_reasons": []})
    _write_json(reports / "prompt_cache_summary_latest.json", {"cache_hit_ratio": 0.5})
    _write_json(reports / "stale_memory_report.json", {"findings": []})
    _write_json(reports / "context_quant_result_latest.json", {"decision": "WARN"})

    mon = TuiProcessMonitor(aiwg_root=aiwg)
    snap = mon.build_process_monitor_snapshot(write_output=True)
    txt = mon.render_monitor_text(snap)

    assert "Current phase: P17" in txt
    assert "Next phase: P18" in txt
    assert (reports / "process_monitor_latest.json").exists()
    assert (reports / "process_monitor_latest.txt").exists()


def test_tui_process_monitor_missing_optional_artifacts_warn(tmp_path: Path):
    aiwg = tmp_path / ".aiwg"
    _write_json(aiwg / "evolution" / "current_position.json", {"current_phase": "P17"})
    _write_json(aiwg / "evolution" / "next_phase_seed.json", {"next_phase": "P18"})

    mon = TuiProcessMonitor(aiwg_root=aiwg)
    snap = mon.build_process_monitor_snapshot(write_output=False)
    assert snap.decision in {"PASS_WITH_WARNINGS", "FAIL"}
    assert snap.warnings
