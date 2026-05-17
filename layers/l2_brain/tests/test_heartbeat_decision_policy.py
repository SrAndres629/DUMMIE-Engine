"""Tests for heartbeat_decision_policy.py — Heartbeat-0"""
import json, tempfile, shutil
from pathlib import Path
from heartbeat_decision_policy import select_next_action, classify_dispatch, block_unsafe_actions


def _setup_reports(tmp: Path, actions: list, readiness_degraded: bool = True):
    reports = tmp / ".aiwg" / "reports"
    reports.mkdir(parents=True)
    (reports / "self_improvement_action_queue.json").write_text(json.dumps({
        "actions": actions,
        "blocked": ["autonomous_scaling"],
        "next": "repair_kuzu_persistence"
    }))
    (reports / "evolution_delta_application_latest.json").write_text(json.dumps({}))
    (reports / "mental_model_truth_hygiene_latest.json").write_text(json.dumps({}))
    
    kuzu_finding = {"id": "score_1_with_degraded_kuzu", "description": "Kuzu degraded"} if readiness_degraded else {"id": "ok", "description": "ok"}
    (reports / "readiness_score_calibration_latest.json").write_text(json.dumps({
        "findings": [kuzu_finding]
    }))


def test_classify_dispatch():
    assert classify_dispatch("repair_kuzu_persistence") == "antigravity"
    assert classify_dispatch("increase_test_coverage") == "codex"
    assert classify_dispatch("unknown_action") == "human_review"


def test_select_next_action_critical_first():
    tmp = Path(tempfile.mkdtemp())
    try:
        actions = [
            {"action_type": "increase_test_coverage", "priority": "high", "status": "proposed"},
            {"action_type": "repair_kuzu_persistence", "priority": "critical", "status": "proposed"},
        ]
        _setup_reports(tmp, actions)
        policy = select_next_action(aiwg_root=tmp / ".aiwg")
        assert policy.selected_action["action_type"] == "repair_kuzu_persistence"
        assert policy.dispatch_recommendation == "antigravity"
    finally:
        shutil.rmtree(tmp)


def test_blocks_autonomous_scaling():
    tmp = Path(tempfile.mkdtemp())
    try:
        actions = [
            {"action_type": "autonomous_scaling", "priority": "critical", "status": "blocked"},
            {"action_type": "increase_test_coverage", "priority": "high", "status": "proposed"}
        ]
        _setup_reports(tmp, actions)
        policy = select_next_action(aiwg_root=tmp / ".aiwg")
        assert policy.selected_action["action_type"] == "increase_test_coverage"
        assert "autonomous_scaling" in policy.blocked_actions
    finally:
        shutil.rmtree(tmp)
