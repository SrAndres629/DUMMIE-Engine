import os
import json
import pytest
from pathlib import Path
from layers.l2_brain.heartbeat_lifecycle_runtime import run_heartbeat

def test_heartbeat_dependency_integration(tmp_path):
    # Set up mock reports for all required heartbeat inputs in the mock reports directory
    reports_dir = tmp_path.joinpath("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Write empty or valid JSONs for canonical observer items to satisfy checklist
    canonical = [
        "self_improvement_action_queue.json",
        "mental_model_truth_hygiene_latest.json",
        "evolution_delta_application_latest.json",
        "readiness_score_calibration_latest.json",
        "memory_spine_entrypoint_latest.json",
        "epistemic_state_latest.json",
        "metacognitive_loop_latest.json",
        "cognitive_bias_report_latest.json",
        "whole_body_scan_latest.json",
        "whole_body_scan_calibration_latest.json",
        "wiring_matrix_latest.json",
        "shadow_runtime_classification_latest.json",
        "test_debt_triage_latest.json"
    ]
    
    for filename in canonical:
        reports_dir.joinpath(filename).write_text(json.dumps({
            "decision": "PASS",
            "findings": [],
            "calibrated_scores": {"overall": 80.0},
            "scan_metrics": {},
            "quarantined": [],
            "actions": [],
            "missing_tests_count": 0,
            "failing_tests_count": 0
        }))
        
    # Execute the integrated heartbeat runtime
    result = run_heartbeat(mode="observe_only", aiwg_root=tmp_path)
    
    # Assert integrated structures exist
    assert result["heartbeat_id"].startswith("hb-")
    assert "dependency_reality" in result
    assert "degraded_capabilities" in result
    assert "toolchain_probe" in result
    assert "runtime_closure_plan" in result
    
    # Check that decisions propagate warning signals safely
    assert result["decision"] in ["PASS", "PASS_WITH_WARNINGS"]
