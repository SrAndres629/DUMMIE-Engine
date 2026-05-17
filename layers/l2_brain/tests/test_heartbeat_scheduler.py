"""Tests for heartbeat_scheduler.py — Heartbeat-0"""
import json, tempfile, shutil
from pathlib import Path
from heartbeat_scheduler import HeartbeatScheduler


def _setup_aiwg(tmp: Path):
    aiwg = tmp / ".aiwg"
    (aiwg / "reports").mkdir(parents=True)
    (aiwg / "heartbeat").mkdir(parents=True)
    (aiwg / "reports" / "self_improvement_action_queue.json").write_text(json.dumps({
        "actions": [{"action_type": "increase_test_coverage", "priority": "high", "status": "proposed"}],
        "blocked": [],
        "next": "increase_test_coverage"
    }))
    (aiwg / "reports" / "readiness_score_calibration_latest.json").write_text(json.dumps({"findings": []}))
    (aiwg / "reports" / "mental_model_truth_hygiene_latest.json").write_text(json.dumps({}))
    (aiwg / "reports" / "evolution_delta_application_latest.json").write_text(json.dumps({}))
    (aiwg / "reports" / "epistemic_state_latest.json").write_text(json.dumps({}))
    (aiwg / "reports" / "cognitive_bias_report_latest.json").write_text(json.dumps({}))
    (aiwg / "reports" / "memory_spine_entrypoint_latest.json").write_text(json.dumps({}))
    (aiwg / "reports" / "metacognitive_loop_latest.json").write_text(json.dumps({}))
    return aiwg


def test_dry_run():
    tmp = Path(tempfile.mkdtemp())
    try:
        aiwg = _setup_aiwg(tmp)
        scheduler = HeartbeatScheduler(aiwg_root=aiwg)
        res = scheduler.dry_run()
        assert res["type"] == "dry_run"
        assert res["would_select"]["action_type"] == "increase_test_coverage"
        assert (aiwg / "reports" / "heartbeat_scheduler_latest.json").exists()
    finally:
        shutil.rmtree(tmp)


def test_run_once():
    tmp = Path(tempfile.mkdtemp())
    try:
        aiwg = _setup_aiwg(tmp)
        scheduler = HeartbeatScheduler(aiwg_root=aiwg)
        res = scheduler.run_once(mode="observe_only")
        assert res["type"] == "run_once"
        assert res["selected_action"]["action_type"] == "increase_test_coverage"
        assert (aiwg / "reports" / "heartbeat_scheduler_latest.json").exists()
    finally:
        shutil.rmtree(tmp)
