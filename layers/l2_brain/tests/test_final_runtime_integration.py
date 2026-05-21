import json
import pytest
from pathlib import Path
from layers.l2_brain.governance.trusted_workstation_mode import run_trusted_workstation_mode
from layers.l2_brain.governance.chaos_regression_testing import run_chaos_regression_tests
from layers.l2_brain.strategic.autonomous_strategic_partner_runtime import run_autonomous_strategic_partner_runtime

def test_final_runtime_integration(tmp_path):
    aiwg = tmp_path / ".aiwg"
    evo = aiwg / "evolution"
    repo = aiwg / "reports"
    evo.mkdir(parents=True)
    repo.mkdir(parents=True)
    
    (evo / "current_position.json").write_text(json.dumps({"current_phase": "P31"}))
    (evo / "next_phase_seed.json").write_text(json.dumps({"next_phase": "PLAN_V1_COMPLETION_REVIEW"}))
    
    # 1. Run TW
    run_trusted_workstation_mode(aiwg_root=aiwg)
    assert (repo / "trusted_workstation_mode_latest.json").exists()
    
    # 2. Run Chaos
    run_chaos_regression_tests(aiwg_root=aiwg)
    assert (repo / "chaos_regression_report_latest.json").exists()
    
    # 3. Pass prerequisites for Auto
    (repo / "mission_coherence_guard_latest.json").write_text(json.dumps({"decision": "PASS"}))
    (repo / "strategic_partner_swarm_latest.json").write_text(json.dumps({"decision": "continue_next_phase"}))
    (repo / "debate_review_latest.json").write_text(json.dumps({"decision": "accept_plan"}))
    (repo / "mission_autonomy_contract_latest.json").write_text(json.dumps({"decision": "PASS"}))
    
    # 4. Run Auto
    res = run_autonomous_strategic_partner_runtime(aiwg_root=aiwg)
    assert res.decision == "complete_plan_v1_review"
