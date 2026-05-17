"""Tests for heartbeat_lifecycle_runtime.py — Heartbeat-0"""
import json, tempfile, shutil
from pathlib import Path
from heartbeat_lifecycle_runtime import run_heartbeat


def _setup_aiwg(tmp: Path, mock_actions: list = None, kuzu_degraded: bool = True):
    aiwg = tmp / ".aiwg"
    (aiwg / "reports").mkdir(parents=True)
    (aiwg / "heartbeat").mkdir(parents=True)
    (aiwg / "mental_models").mkdir(parents=True)

    # Write a mock Python file so polyglot probe PASSes
    (tmp / "mock_app.py").write_text("print('hello')", encoding="utf-8")

    # Seed mock scanner files so context circulation & mental model compile successfully
    scan = {
        "overall_coherence_score": 55.0,
        "systemic_coherence": 55.0,
        "scan_metrics": {
            "total_files": 100,
            "shadow_modules": 0,
            "orphaned_tests": 0,
            "stale_reports": 0,
            "unvalidated_specs": 0
        }
    }
    (aiwg / "reports" / "whole_body_scan_latest.json").write_text(json.dumps(scan), encoding="utf-8")
    
    cal = {
        "decision": "PASS",
        "calibration_score": 100
    }
    (aiwg / "reports" / "whole_body_scan_calibration_latest.json").write_text(json.dumps(cal), encoding="utf-8")
    
    wir = {
        "decision": "PASS",
        "nodes": [],
        "edges": []
    }
    (aiwg / "reports" / "wiring_matrix_latest.json").write_text(json.dumps(wir), encoding="utf-8")
    
    sha = {
        "decision": "PASS",
        "findings": []
    }
    (aiwg / "reports" / "shadow_runtime_classification_latest.json").write_text(json.dumps(sha), encoding="utf-8")

    # Readiness scoring
    kuzu_finding = {"id": "score_1_with_degraded_kuzu", "description": "Kuzu degraded"} if kuzu_degraded else {"id": "ok", "description": "ok"}
    (aiwg / "reports" / "readiness_score_calibration_latest.json").write_text(json.dumps({
        "findings": [kuzu_finding],
        "calibrated_scores": {"overall": 70.57}
    }))

    # Self-improvement queue
    actions = mock_actions or [
        {"action_id": "act-1", "action_type": "repair_kuzu_persistence", "priority": "critical", "status": "proposed"},
        {"action_id": "act-2", "action_type": "autonomous_scaling", "priority": "critical", "status": "blocked"},
        {"action_id": "act-3", "action_type": "increase_test_coverage", "priority": "high", "status": "proposed"},
    ]
    (aiwg / "reports" / "self_improvement_action_queue.json").write_text(json.dumps({
        "actions": actions,
        "blocked": ["autonomous_scaling"],
        "next": "repair_kuzu_persistence"
    }))

    # Minimal mental model hygiene latest
    (aiwg / "reports" / "mental_model_truth_hygiene_latest.json").write_text(json.dumps({
        "summary": {"quarantined_count": 0, "needs_review_count": 0}
    }))

    # Minimal evolution delta application
    (aiwg / "reports" / "evolution_delta_application_latest.json").write_text(json.dumps({
        "decision": "PASS",
        "actions": actions,
        "blocked_actions": ["autonomous_scaling"]
    }))

    # Epistemic, loop, etc. fallback files
    (aiwg / "reports" / "epistemic_state_latest.json").write_text(json.dumps({"decision": "PASS", "confidence": 0.9}))
    (aiwg / "reports" / "cognitive_bias_report_latest.json").write_text(json.dumps({"decision": "PASS", "findings": []}))
    (aiwg / "reports" / "memory_spine_entrypoint_latest.json").write_text(json.dumps({"status": "PASS"}))
    (aiwg / "reports" / "metacognitive_loop_latest.json").write_text(json.dumps({"decision": "PASS"}))

    return aiwg


def test_heartbeat_runs_in_observe_only_mode():
    tmp = Path(tempfile.mkdtemp())
    try:
        aiwg = _setup_aiwg(tmp)
        res = run_heartbeat(mode="observe_only", aiwg_root=aiwg)
        assert res["heartbeat_id"].startswith("hb-")
        assert res["mode"] == "observe_only"
        assert res["decision"] in ("PASS_WITH_WARNINGS", "NEEDS_HUMAN_REVIEW")
        assert "evidence_refs" in res
    finally:
        shutil.rmtree(tmp)


def test_heartbeat_respects_blocked_actions():
    tmp = Path(tempfile.mkdtemp())
    try:
        aiwg = _setup_aiwg(tmp, mock_actions=[
            {"action_id": "act-1", "action_type": "autonomous_scaling", "priority": "critical", "status": "blocked"}
        ])
        res = run_heartbeat(mode="observe_only", aiwg_root=aiwg)
        assert res["selected_action"]["action_type"] != "autonomous_scaling"
        assert "autonomous_scaling" in res["blocked_actions"]
    finally:
        shutil.rmtree(tmp)


def test_outputs_written():
    tmp = Path(tempfile.mkdtemp())
    try:
        aiwg = _setup_aiwg(tmp)
        run_heartbeat(mode="observe_only", aiwg_root=aiwg)
        assert (aiwg / "reports" / "heartbeat_latest.json").exists()
        assert (aiwg / "reports" / "heartbeat_latest.md").exists()
        assert (aiwg / "heartbeat" / "heartbeat_ledger.jsonl").exists()
        assert (aiwg / "heartbeat" / "next_heartbeat_seed.json").exists()
    finally:
        shutil.rmtree(tmp)
