import json
import pytest
from pathlib import Path
from layers.l2_brain.mission.debate_review_runtime import DebateReviewRuntime

@pytest.fixture
def debate_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    evo = aiwg / "evolution"
    repo = aiwg / "reports"
    evo.mkdir(parents=True)
    repo.mkdir(parents=True)
    
    (evo / "current_position.json").write_text(json.dumps({"current_phase": "P26"}))
    (evo / "next_phase_seed.json").write_text(json.dumps({"next_phase": "P27"}))
    (repo / "mission_plan_latest.json").write_text(json.dumps({"mission_id": "MISSION_P27", "l3_microphases": [{"microphase_id": "L3_1", "tests_to_run": ["test.py"]}]}))
    (repo / "strategic_partner_swarm_latest.json").write_text(json.dumps({"decision": "continue_next_phase", "confidence": 0.8}))
    (repo / "mission_coherence_guard_latest.json").write_text(json.dumps({"decision": "PASS"}))
    
    return aiwg

def test_debate_review_creates_all_roles(debate_env):
    runtime = DebateReviewRuntime(aiwg_root=debate_env)
    result = runtime.run_debate()
    assert len(result.roles) == 6
    assert any(r.role == "skeptic" for r in result.roles)
    assert result.decision == "accept_plan"

def test_debate_blocks_on_coherence_failure(debate_env):
    (debate_env / "reports" / "mission_coherence_guard_latest.json").write_text(json.dumps({"decision": "FAIL"}))
    runtime = DebateReviewRuntime(aiwg_root=debate_env)
    result = runtime.run_debate()
    assert result.decision == "block"
    assert result.judge_verdict["verdict"] == "block"

def test_debate_flags_missing_tests(debate_env):
    (debate_env / "reports" / "mission_plan_latest.json").write_text(json.dumps({"l3_microphases": [{"microphase_id": "L3_1", "tests_to_run": []}]}))
    runtime = DebateReviewRuntime(aiwg_root=debate_env)
    result = runtime.run_debate()
    assert any("missing_tests" in obj for obj in result.objections)
