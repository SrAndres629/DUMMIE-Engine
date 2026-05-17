"""Integration tests for Whole-Body Scan metrics inside recurring Heartbeat cycles."""

import json
from pathlib import Path
from heartbeat_lifecycle_runtime import run_heartbeat


def test_whole_body_integration_heartbeat_execution(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    # 1. Write mock scanner reports
    scan_data = {
        "overall_coherence_score": 92.5,
        "metrics": {
            "active_modules_count": 48,
            "shadow_modules_count": 0,
            "orphaned_tests_count": 0,
            "stale_reports_count": 0,
            "unvalidated_specs_count": 0
        }
    }
    (reports / "whole_body_scan_latest.json").write_text(json.dumps(scan_data), encoding="utf-8")

    calibration_data = {
        "decision": "PASS",
        "scan_metrics": {
            "active_modules": 48,
            "shadow_modules": 0,
            "orphaned_tests": 0,
            "stale_reports": 0,
            "unvalidated_specs": 0
        },
        "test_reconciliation": {
            "suite_total_tests": 46,
            "reconciled": True
        }
    }
    (reports / "whole_body_scan_calibration_latest.json").write_text(json.dumps(calibration_data), encoding="utf-8")

    wiring_data = {
        "decision": "PASS",
        "nodes": [],
        "edges": [],
        "anomaly_summary": {
            "unwired_source_modules": [],
            "source_without_tests": []
        }
    }
    (reports / "wiring_matrix_latest.json").write_text(json.dumps(wiring_data), encoding="utf-8")

    shadow_data = {
        "decision": "PASS",
        "findings": []
    }
    (reports / "shadow_runtime_classification_latest.json").write_text(json.dumps(shadow_data), encoding="utf-8")

    # Write other heartbeat-required files so it doesn't fail
    (reports / "self_improvement_action_queue.json").write_text(json.dumps({"actions": [], "blocked": []}), encoding="utf-8")
    (reports / "mental_model_truth_hygiene_latest.json").write_text(json.dumps({"summary": {"quarantined_count": 0}}), encoding="utf-8")
    (reports / "readiness_score_calibration_latest.json").write_text(json.dumps({"calibrated_scores": {"overall": 100.0}}), encoding="utf-8")
    (reports / "test_debt_triage_latest.json").write_text(json.dumps({"missing_tests_count": 0, "failing_tests_count": 0}), encoding="utf-8")

    # Run heartbeat
    res = run_heartbeat(mode="observe_only", aiwg_root=tmp_path)

    # Assert observation contains whole body scan metrics
    obs = res["observation"]
    assert "whole_body_scan" in obs
    wbs = obs["whole_body_scan"]
    assert wbs["overall_coherence_score"] == 92.5
    assert wbs["calibration_decision"] == "PASS"
    assert wbs["wiring_matrix_decision"] == "PASS"
    assert wbs["shadow_classification_decision"] == "PASS"

    assert res["decision"] in ("PASS", "PASS_WITH_WARNINGS")
