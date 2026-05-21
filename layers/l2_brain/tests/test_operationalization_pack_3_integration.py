"""Integration tests for Operationalization Pack 3."""
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

from layers.l2_brain.governance.readiness_score_calibrator import run_readiness_score_calibration
from layers.l2_brain.memory.memory_spine_entrypoint import run_memory_spine_entrypoint_demo
from layers.l2_brain.context.token_economy_benchmark import run_token_economy_benchmark
from layers.l2_brain.governance.entrypoint_enforcement_auditor import run_entrypoint_enforcement_audit


@pytest.fixture
def pack3_repo(tmp_path):
    """Create a minimal repo for Pack 3 integration tests."""
    aiwg = tmp_path / ".aiwg"
    reports = aiwg / "reports"
    intel = aiwg / "repo_intelligence"
    sessions = aiwg / "sessions"
    reports.mkdir(parents=True)
    intel.mkdir(parents=True)
    sessions.mkdir(parents=True)

    # Create memory sync report (DEGRADED)
    (reports / "memory_spine_sync_latest.json").write_text(
        json.dumps({"db_status": "DEGRADED"}), encoding="utf-8"
    )

    # Create minimal CLI and control plane files
    l2 = tmp_path / "layers" / "l2_brain"
    l2.mkdir(parents=True)
    (l2 / "cli_control_plane.py").write_text("# dummie_chat_cli\n", encoding="utf-8")
    (l2 / "dummie_chat_cli.py").write_text(
        "from memory_spine_entrypoint import retrieve_memory\n"
        "ContextEnforcementGate\n_latest.json\n",
        encoding="utf-8"
    )

    return tmp_path


class TestPack3Integration:
    def test_calibration_produces_valid_json(self, pack3_repo):
        """Calibration result must be valid JSON-serializable."""
        report = run_readiness_score_calibration(repo_root=pack3_repo)
        data = report.to_dict()
        serialized = json.dumps(data)
        parsed = json.loads(serialized)
        assert "decision" in parsed

    def test_memory_spine_produces_valid_json(self, pack3_repo):
        """Memory spine result must be valid JSON-serializable."""
        result = run_memory_spine_entrypoint_demo("test", repo_root=pack3_repo)
        data = result.to_dict()
        serialized = json.dumps(data)
        parsed = json.loads(serialized)
        assert "decision" in parsed

    def test_token_benchmark_produces_valid_json(self, pack3_repo):
        """Token benchmark result must be valid JSON-serializable."""
        report = run_token_economy_benchmark(repo_root=pack3_repo)
        data = report.to_dict()
        serialized = json.dumps(data)
        parsed = json.loads(serialized)
        assert "decision" in parsed

    def test_entrypoint_audit_produces_valid_json(self, pack3_repo):
        """Entrypoint audit result must be valid JSON-serializable."""
        result = run_entrypoint_enforcement_audit(repo_root=pack3_repo)
        serialized = json.dumps(result)
        parsed = json.loads(serialized)
        assert "decision" in parsed

    def test_integration_chain(self, pack3_repo):
        """All Pack 3 modules should run in sequence without errors."""
        cal = run_readiness_score_calibration(repo_root=pack3_repo)
        assert cal.decision in ("PASS", "PASS_WITH_WARNINGS")

        mem = run_memory_spine_entrypoint_demo("what should I do next?", repo_root=pack3_repo)
        assert mem.decision in ("PASS", "PASS_WITH_WARNINGS")

        bench = run_token_economy_benchmark(repo_root=pack3_repo)
        assert bench.decision in ("PASS", "PASS_WITH_WARNINGS")

        audit = run_entrypoint_enforcement_audit(repo_root=pack3_repo)
        assert audit["decision"] in ("PASS", "PASS_WITH_WARNINGS")

    def test_degraded_kuzu_flows_through(self, pack3_repo):
        """When Kuzu is DEGRADED, calibrator should detect it via memory spine."""
        mem = run_memory_spine_entrypoint_demo("status", repo_root=pack3_repo)
        assert mem.status == "DEGRADED_WITH_FILE_BACKED_MEMORY"

        cal = run_readiness_score_calibration(repo_root=pack3_repo)
        assert cal.calibrated_scores["memory_spine_readiness"] < 10.0
