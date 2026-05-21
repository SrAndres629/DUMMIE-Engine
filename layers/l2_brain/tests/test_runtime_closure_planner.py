import os
import json
from pathlib import Path
from layers.l2_brain.governance.runtime_dependency_auditor import run_runtime_dependency_audit
from layers.l2_brain.governance.degraded_capability_registry import run_degraded_capability_registry
from layers.l2_brain.runtime_closure_planner import run_runtime_closure_plan

def test_runtime_closure_planner_execution(tmp_path):
    # Pre-generate dependency and registry audits
    run_runtime_dependency_audit(aiwg_root=str(tmp_path))
    run_degraded_capability_registry(aiwg_root=str(tmp_path))
    
    # Execute the planner
    res = run_runtime_closure_plan(aiwg_root=str(tmp_path))
    
    assert "decision" in res
    assert "actions" in res
    
    # Enforce strict safety constraints
    for action in res["actions"]:
        if action["action_type"] == "install_dependency":
            assert action["can_execute_now"] is False
            assert action["requires_human_approval"] is True
            
    latest_json = tmp_path.joinpath(".aiwg/reports/runtime_closure_plan_latest.json")
    assert latest_json.exists()
