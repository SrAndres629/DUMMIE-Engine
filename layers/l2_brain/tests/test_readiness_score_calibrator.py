"""Tests for ReadinessScoreCalibrator — Pack 3 Module 1."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
L2 = ROOT / "layers" / "l2_brain"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(L2) not in sys.path:
    sys.path.insert(0, str(L2))

from layers.l2_brain.governance.readiness_score_calibrator import (
    ReadinessCalibrationFinding,
    ReadinessCalibrationReport,
    ReadinessScoreCalibrator,
    run_readiness_score_calibration,
)


@pytest.fixture
def aiwg_dir(tmp_path):
    """Create a minimal .aiwg structure for testing."""
    aiwg = tmp_path / ".aiwg"
    reports = aiwg / "reports"
    reports.mkdir(parents=True)
    return aiwg


class TestReadinessScoreCalibrator:
    def test_downgrades_kuzu_degraded(self, aiwg_dir):
        """If Kuzu is DEGRADED, memory_spine_readiness must be < 10."""
        reports = aiwg_dir / "reports"
        (reports / "memory_spine_sync_latest.json").write_text(
            json.dumps({"db_status": "DEGRADED"}), encoding="utf-8"
        )
        cal = ReadinessScoreCalibrator(repo_root=aiwg_dir.parent, aiwg_root=".aiwg")
        report = cal.run_calibration()

        assert report.calibrated_scores["memory_spine_readiness"] < 10.0
        assert any(f.id == "score_1_with_degraded_kuzu" for f in report.findings)

    def test_does_not_allow_perfect_score_without_benchmark(self, aiwg_dir):
        """If no token benchmark exists, token_economy_readiness must be < 10."""
        cal = ReadinessScoreCalibrator(repo_root=aiwg_dir.parent, aiwg_root=".aiwg")
        report = cal.run_calibration()

        assert report.calibrated_scores["token_economy_readiness"] < 10.0
        assert any(f.id == "score_1_without_token_benchmark_evidence" for f in report.findings)

    def test_perfect_score_when_no_issues(self, aiwg_dir):
        """If everything is fine, scores should be 10."""
        reports = aiwg_dir / "reports"
        (reports / "memory_spine_sync_latest.json").write_text(
            json.dumps({"db_status": "READY"}), encoding="utf-8"
        )
        (reports / "dummie_chat_cli_latest.json").write_text(
            json.dumps({"memory_spine": {"status": "READY"}, "memory_spine_used": True}), encoding="utf-8"
        )
        (reports / "token_economy_benchmark_latest.json").write_text(
            json.dumps({"decision": "PASS"}), encoding="utf-8"
        )
        (reports / "context_coverage_latest.json").write_text(
            json.dumps({"metrics": []}), encoding="utf-8"
        )
        cal = ReadinessScoreCalibrator(repo_root=aiwg_dir.parent, aiwg_root=".aiwg")
        report = cal.run_calibration()

        assert report.decision == "PASS"
        assert report.calibrated_scores["memory_spine_readiness"] == 10.0

    def test_advisory_only_penalty(self, aiwg_dir):
        """Advisory-only capabilities should penalize autonomy readiness."""
        reports = aiwg_dir / "reports"
        (reports / "plan_v1_runtime_capability_scorecard.json").write_text(
            json.dumps({"capabilities": [
                {"name": "test_cap", "operational_mode": "advisory_only"}
            ]}), encoding="utf-8"
        )
        (reports / "token_economy_benchmark_latest.json").write_text(
            json.dumps({"decision": "PASS"}), encoding="utf-8"
        )
        cal = ReadinessScoreCalibrator(repo_root=aiwg_dir.parent, aiwg_root=".aiwg")
        report = cal.run_calibration()

        assert any(f.id == "score_1_with_advisory_only_capability" for f in report.findings)

    def test_report_writes_json(self, aiwg_dir):
        """Calibration should write valid JSON report."""
        cal = ReadinessScoreCalibrator(repo_root=aiwg_dir.parent, aiwg_root=".aiwg")
        cal.run_calibration()

        path = aiwg_dir / "reports" / "readiness_score_calibration_latest.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "decision" in data
        assert "calibrated_scores" in data

    def test_report_writes_md(self, aiwg_dir):
        """Calibration should write markdown report."""
        cal = ReadinessScoreCalibrator(repo_root=aiwg_dir.parent, aiwg_root=".aiwg")
        cal.run_calibration()

        path = aiwg_dir / "reports" / "readiness_score_calibration_latest.md"
        assert path.exists()
        assert "Readiness Score Calibration" in path.read_text(encoding="utf-8")

    def test_run_function(self, aiwg_dir, monkeypatch):
        """run_readiness_score_calibration should work."""
        monkeypatch.chdir(aiwg_dir.parent)
        report = run_readiness_score_calibration(repo_root=aiwg_dir.parent)
        assert isinstance(report, ReadinessCalibrationReport)
