import json
from pathlib import Path

from layers.l6_skin.dashboard_renderer import DashboardRenderer


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_dashboard_renderer_build_and_write(tmp_path: Path):
    aiwg = tmp_path / ".aiwg"
    reports = aiwg / "reports"

    _write_json(aiwg / "evolution" / "current_position.json", {"plan": "DUMMIE", "current_phase": "P17"})
    _write_json(aiwg / "evolution" / "next_phase_seed.json", {"next_phase": "P18"})
    _write_json(reports / "restart_integration_gate_latest.json", {"decision": "PASS"})
    _write_json(reports / "evolution_flywheel_latest.json", {"decision": "continue_next_phase"})
    _write_json(reports / "context_efficiency_benchmark_latest.json", {"decision": "IMPROVED"})
    _write_json(reports / "prompt_cache_summary_latest.json", {"cache_hit_ratio": 0.42})
    _write_json(reports / "stale_memory_report.json", {"findings": []})
    _write_json(reports / "prompt_frame_latest.json", {"frame_id": "f-1"})

    r = DashboardRenderer(aiwg_root=aiwg)
    state = r.build_dashboard_state()
    html = r.render_dashboard_html(state)
    r.write_dashboard_outputs(state)

    assert "Current Phase" in html
    assert "Flywheel" in html
    assert (reports / "dashboard_l6_latest.json").exists()
    assert (reports / "dashboard_l6_latest.html").exists()

    json.loads((reports / "dashboard_l6_latest.json").read_text(encoding="utf-8"))
