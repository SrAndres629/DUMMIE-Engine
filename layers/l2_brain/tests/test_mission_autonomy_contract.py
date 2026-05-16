import json
import pytest
from pathlib import Path
from layers.l2_brain.mission_autonomy_contract import MissionAutonomyContract, AutonomyRequest

@pytest.fixture
def autonomy_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    evo = aiwg / "evolution"
    repo = aiwg / "reports"
    evo.mkdir(parents=True)
    repo.mkdir(parents=True)
    
    (evo / "current_position.json").write_text(json.dumps({"current_phase": "P26"}))
    (repo / "debate_review_latest.json").write_text(json.dumps({"decision": "accept_plan"}))
    
    return aiwg

def test_autonomy_allows_safe_advisory(autonomy_env):
    contract = MissionAutonomyContract(aiwg_root=autonomy_env)
    req = AutonomyRequest(request_id="r1", mission_id="M1", requested_scope="ADVISORY_ONLY", requested_action="test")
    res = contract.evaluate_request(req)
    assert res.decision == "ALLOW"
    assert res.can_execute_now == True

def test_autonomy_blocks_env_access(autonomy_env):
    contract = MissionAutonomyContract(aiwg_root=autonomy_env)
    req = AutonomyRequest(request_id="r2", mission_id="M1", requested_scope="READ_ONLY_ANALYSIS", requested_action="read", target_paths=[".env"])
    res = contract.evaluate_request(req)
    assert res.decision == "BLOCK"
    assert "credentials/env access" in res.reason

def test_autonomy_requires_approval_for_mutation(autonomy_env):
    contract = MissionAutonomyContract(aiwg_root=autonomy_env)
    req = AutonomyRequest(request_id="r3", mission_id="M1", requested_scope="HUMAN_APPROVED_WORKSPACE_EDIT", requested_action="edit", requires_workspace_mutation=True)
    res = contract.evaluate_request(req)
    assert res.decision == "ALLOW_WITH_HUMAN_APPROVAL"
    assert "human_approval" in res.required_authorizations

def test_autonomy_denies_network(autonomy_env):
    contract = MissionAutonomyContract(aiwg_root=autonomy_env)
    req = AutonomyRequest(request_id="r4", mission_id="M1", requested_scope="ADVISORY_ONLY", requested_action="post", requires_network=True)
    res = contract.evaluate_request(req)
    assert res.decision == "DENY"
    assert "network" in res.reason
