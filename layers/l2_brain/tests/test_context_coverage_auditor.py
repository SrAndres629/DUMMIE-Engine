from __future__ import annotations

import json
from pathlib import Path

import pytest
from context_coverage_auditor import ContextCoverageAuditor


@pytest.fixture
def temp_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    aiwg = repo / ".aiwg"
    aiwg.mkdir()
    (aiwg / "reports").mkdir()
    intel = aiwg / "repo_intelligence"
    intel.mkdir()
    
    inventory = {
        "files": [
            {"path": "layers/l2_brain/daemon.py", "is_runtime": True, "language": "python"},
            {"path": "doc/specs/test.md", "is_spec": True}
        ]
    }
    (intel / "repo_inventory.json").write_text(json.dumps(inventory))
    
    return repo


def test_context_coverage_audit_flow(temp_repo):
    auditor = ContextCoverageAuditor(repo_root=temp_repo, aiwg_root=".aiwg")
    report = auditor.run_audit()
    
    assert report["decision"] == "PASS"
    metrics = report["metrics"]
    
    # Summary metric should exist
    summary = next(m for m in metrics if m["category"] == "DOSSIER_SUMMARY")
    assert summary["status"] == "PARTIAL" # 0/1 covered
    
    # Check report exists
    report_path = temp_repo / ".aiwg" / "reports" / "context_coverage_latest.json"
    assert report_path.exists()
