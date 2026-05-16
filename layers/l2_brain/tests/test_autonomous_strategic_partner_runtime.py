import json
import pytest
from pathlib import Path
from layers.l2_brain.autonomous_strategic_partner_runtime import AutonomousStrategicPartnerRuntime

@pytest.fixture
def auto_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    evo = aiwg / "evolution"
    repo = aiwg / "reports"
    evo.mkdir(parents=True)
    repo.mkdir(parents=True)
    
    (evo / "current_position.json").write_text(json.dumps({"current_phase": "P31"}))
    (evo / "next_phase_seed.json").write_text(json.dumps({"next_phase": "PLAN_V1_COMPLETION_REVIEW"}))
    
    # PASS all gates
    (repo / "mission_coherence_guard_latest.json").write_text(json.dumps({"decision": "PASS"}))
    (repo / "chaos_regression_report_latest.json").write_text(json.dumps({"decision": "PASS"}))
    (repo / "debate_review_latest.json").write_text(json.dumps({"decision": "accept_plan"}))
    (repo / "mission_autonomy_contract_latest.json").write_text(json.dumps({"decision": "PASS"}))
    
    return aiwg

def test_auto_runtime_completes_plan_v1(auto_env):
    runtime = AutonomousStrategicPartnerRuntime(aiwg_root=auto_env)
    res = runtime.run_strategic_runtime()
    assert res.decision == "complete_plan_v1_review"
    assert res.plan_v1_completion_status == "complete"

def test_auto_runtime_blocks_on_chaos_fail(auto_env):
    (auto_env / "reports" / "chaos_regression_report_latest.json").write_text(json.dumps({"decision": "FAIL"}))
    runtime = AutonomousStrategicPartnerRuntime(aiwg_root=auto_env)
    res = runtime.run_strategic_runtime()
    assert res.decision == "block_due_to_safety"
    assert "chaos_regression_failure" in res.blocking_reasons

def test_auto_runtime_requests_human_review_on_debate_obj(auto_env):
    (auto_env / "reports" / "debate_review_latest.json").write_text(json.dumps({"decision": "request_human_review"}))
    runtime = AutonomousStrategicPartnerRuntime(aiwg_root=auto_env)
    res = runtime.run_strategic_runtime()
    assert res.decision == "request_human_review"
