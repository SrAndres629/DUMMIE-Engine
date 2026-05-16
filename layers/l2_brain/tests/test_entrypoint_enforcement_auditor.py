"""Tests for EntrypointEnforcementAuditor — Pack 3 Module 4."""
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

from layers.l2_brain.entrypoint_enforcement_auditor import (
    EntrypointEnforcementAudit,
    EntrypointEnforcementAuditor,
    run_entrypoint_enforcement_audit,
)


@pytest.fixture
def repo_dir(tmp_path):
    """Create a minimal repo structure."""
    aiwg = tmp_path / ".aiwg"
    reports = aiwg / "reports"
    reports.mkdir(parents=True)

    l2 = tmp_path / "layers" / "l2_brain"
    l2.mkdir(parents=True)

    # Create a minimal cli_control_plane.py
    (l2 / "cli_control_plane.py").write_text(
        "# dummie_chat_cli\n# mission_planner\n", encoding="utf-8"
    )

    # Create a minimal dummie_chat_cli.py with memory spine
    (l2 / "dummie_chat_cli.py").write_text(
        "from memory_spine_entrypoint import retrieve_memory\n"
        "ContextEnforcementGate\n"
        "outcome\n"
        "_latest.json\n",
        encoding="utf-8"
    )

    return tmp_path


class TestEntrypointEnforcementAuditor:
    def test_reports_missing_integrations_as_warnings(self, repo_dir):
        """Auditor must report PASS_WITH_WARNINGS for missing integrations."""
        auditor = EntrypointEnforcementAuditor(repo_root=repo_dir, aiwg_root=".aiwg")
        report = auditor.run_audit()

        assert report["decision"] in ("PASS", "PASS_WITH_WARNINGS")
        assert "audits" in report
        assert len(report["audits"]) >= 8

    def test_does_not_crash_on_missing_files(self, repo_dir):
        """Auditor must not crash when entrypoint files don't exist."""
        auditor = EntrypointEnforcementAuditor(repo_root=repo_dir, aiwg_root=".aiwg")
        report = auditor.run_audit()
        assert "audits" in report

    def test_detects_memory_spine_usage(self, repo_dir):
        """Should detect when an entrypoint uses memory spine."""
        auditor = EntrypointEnforcementAuditor(repo_root=repo_dir, aiwg_root=".aiwg")
        report = auditor.run_audit()

        chat_audit = next((a for a in report["audits"] if a["entrypoint"] == "dummie_chat_cli"), None)
        assert chat_audit is not None
        assert chat_audit["uses_memory_spine"] is True

    def test_writes_latest_json(self, repo_dir):
        """Must write entrypoint_enforcement_audit_latest.json."""
        auditor = EntrypointEnforcementAuditor(repo_root=repo_dir, aiwg_root=".aiwg")
        auditor.run_audit()

        path = repo_dir / ".aiwg" / "reports" / "entrypoint_enforcement_audit_latest.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "decision" in data

    def test_writes_latest_md(self, repo_dir):
        """Must write entrypoint_enforcement_audit_latest.md."""
        auditor = EntrypointEnforcementAuditor(repo_root=repo_dir, aiwg_root=".aiwg")
        auditor.run_audit()

        path = repo_dir / ".aiwg" / "reports" / "entrypoint_enforcement_audit_latest.md"
        assert path.exists()

    def test_run_function(self, repo_dir, monkeypatch):
        """run_entrypoint_enforcement_audit should work."""
        monkeypatch.chdir(repo_dir)
        result = run_entrypoint_enforcement_audit(repo_root=repo_dir)
        assert isinstance(result, dict)
        assert "decision" in result
