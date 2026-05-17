"""Tests for Whole-Body Scan Calibrator."""

import json
from pathlib import Path
import pytest
from whole_body_scan_calibrator import run_whole_body_scan_calibration


def test_whole_body_scan_calibrator_execution(tmp_path, monkeypatch):
    # Setup simulated workspace
    reports = tmp_path / ".aiwg" / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    # Create mock scan output
    scan_data = {
        "timestamp": "2026-05-17T00:00:00Z",
        "overall_coherence_score": 75.0,
        "profiling_profile": "normal",
        "report_version": "1.0",
        "freshness_timestamp": "2026-05-17T00:00:00Z",
        "runtime_seconds": 1.5,
        "reproducibility_hash": "abc123hash",
        "metrics": {
            "total_python_files": 12,
            "active_modules_count": 10,
            "shadow_modules_count": 2,
            "orphaned_tests_count": 1,
            "stale_reports_count": 0,
            "unvalidated_specs_count": 3
        },
        "findings": {},
        "matrix": {}
    }
    (reports / "whole_body_scan_latest.json").write_text(json.dumps(scan_data), encoding="utf-8")

    # Create mock readiness report
    readiness_data = {
        "calibrated_scores": {"overall": 80.0}
    }
    (reports / "readiness_score_calibration_latest.json").write_text(json.dumps(readiness_data), encoding="utf-8")

    # Create mock test debt report
    triage_data = {
        "failing_tests_count": 0
    }
    (reports / "test_debt_triage_latest.json").write_text(json.dumps(triage_data), encoding="utf-8")

    # Run calibration
    res = run_whole_body_scan_calibration(aiwg_root=tmp_path)

    assert res["decision"] == "PASS_WITH_WARNINGS"
    assert res["scan_metrics"]["active_modules"] == 10
    assert res["scan_metrics"]["shadow_modules"] == 2
    assert res["scan_metrics"]["orphaned_tests"] == 1
    assert res["scan_metrics"]["unvalidated_specs"] == 3
    assert res["test_reconciliation"]["reconciled"] is True

    # Assert report files created
    assert (reports / "whole_body_scan_calibration_latest.json").exists()
    assert (reports / "whole_body_scan_calibration_latest.md").exists()
