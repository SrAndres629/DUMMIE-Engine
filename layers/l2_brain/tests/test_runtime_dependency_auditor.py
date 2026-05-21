import os
import json
from pathlib import Path
from layers.l2_brain.governance.runtime_dependency_auditor import run_runtime_dependency_audit

def test_runtime_dependency_audit_execution(tmp_path):
    # Execute the audit in dry-run/read-only mode using a temporary aiwg root
    res = run_runtime_dependency_audit(aiwg_root=str(tmp_path))
    
    assert "decision" in res
    assert "dependencies" in res
    assert "missing_dependencies" in res
    assert "simulated_capabilities" in res
    
    # Assert JSON file was written correctly
    latest_json = tmp_path.joinpath(".aiwg/reports/runtime_dependency_audit_latest.json")
    assert latest_json.exists()
    
    with open(latest_json, "r") as f:
        data = json.load(f)
    assert data["decision"] == res["decision"]
