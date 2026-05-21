import os
import json
from pathlib import Path
from layers.l2_brain.governance.runtime_dependency_auditor import run_runtime_dependency_audit
from layers.l2_brain.governance.degraded_capability_registry import run_degraded_capability_registry

def test_degraded_capability_registry_execution(tmp_path):
    # Pre-generate dependency audit report
    run_runtime_dependency_audit(aiwg_root=str(tmp_path))
    
    # Execute the registry generator
    res = run_degraded_capability_registry(aiwg_root=str(tmp_path))
    
    assert "decision" in res
    assert "capabilities" in res
    
    # Check that Kùzu capability exists and has correct metadata properties
    kuzu_cap = None
    for cap in res["capabilities"]:
        if cap["capability_id"] == "kuzu_4dtes_persistence":
            kuzu_cap = cap
            break
            
    assert kuzu_cap is not None
    assert "claimed_status" in kuzu_cap
    assert "actual_status" in kuzu_cap
    assert "required_dependencies" in kuzu_cap
    assert "required_verification" in kuzu_cap
    
    # Verify report persistence
    latest_json = tmp_path.joinpath(".aiwg/reports/degraded_capability_registry_latest.json")
    assert latest_json.exists()
