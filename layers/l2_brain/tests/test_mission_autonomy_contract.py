import json
import pytest
from pathlib import Path
from layers.l2_brain.mission.mission_autonomy_contract import MissionAutonomyContract, AutonomyRequest

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

def test_autonomy_obsoletes_read_only_analysis(autonomy_env):
    contract = MissionAutonomyContract(aiwg_root=autonomy_env)
    req = AutonomyRequest(request_id="r1b", mission_id="M1", requested_scope="READ_ONLY_ANALYSIS", requested_action="inspect")
    res = contract.evaluate_request(req)
    assert res.decision == "DENY"
    assert res.granted_scope == "DENIED"
    assert "obsolete" in res.reason

def test_autonomy_allows_analyze_plan_and_spec_authoring(autonomy_env):
    contract = MissionAutonomyContract(aiwg_root=autonomy_env)

    analyze = contract.evaluate_request(
        AutonomyRequest(request_id="r1c", mission_id="M1", requested_scope="ANALYZE_PLAN", requested_action="inspect and plan")
    )
    spec = contract.evaluate_request(
        AutonomyRequest(request_id="r1d", mission_id="M1", requested_scope="SPEC_AUTHORING", requested_action="write spec")
    )

    assert analyze.decision == "ALLOW"
    assert analyze.can_execute_now is True
    assert spec.decision == "ALLOW"
    assert spec.can_execute_now is True

def test_autonomy_allows_workspace_write_with_verification_evidence(autonomy_env):
    contract = MissionAutonomyContract(aiwg_root=autonomy_env)
    req = AutonomyRequest(
        request_id="r1e",
        mission_id="M1",
        requested_scope="WORKSPACE_WRITE",
        requested_action="edit governed source",
        target_paths=["layers/l2_brain/mission/mission_autonomy_contract.py"],
        evidence_refs=["uv run pytest -q layers/l2_brain/tests/test_mission_autonomy_contract.py"],
        requires_workspace_mutation=True,
    )

    res = contract.evaluate_request(req)

    assert res.decision == "ALLOW_WITH_VERIFICATION"
    assert res.granted_scope == "WORKSPACE_WRITE"
    assert res.can_execute_now is True
    assert "verification_required" in res.required_authorizations

def test_autonomy_blocks_env_access(autonomy_env):
    contract = MissionAutonomyContract(aiwg_root=autonomy_env)
    req = AutonomyRequest(request_id="r2", mission_id="M1", requested_scope="ANALYZE_PLAN", requested_action="read", target_paths=[".env"])
    res = contract.evaluate_request(req)
    assert res.decision == "BLOCK"
    assert "credentials/env access" in res.reason

def test_autonomy_requires_approval_for_mutation(autonomy_env):
    contract = MissionAutonomyContract(aiwg_root=autonomy_env)
    req = AutonomyRequest(request_id="r3", mission_id="M1", requested_scope="WORKSPACE_WRITE", requested_action="edit", requires_workspace_mutation=True)
    res = contract.evaluate_request(req)
    assert res.decision == "ALLOW_WITH_HUMAN_APPROVAL"
    assert "human_approval" in res.required_authorizations

def test_autonomy_denies_network(autonomy_env):
    contract = MissionAutonomyContract(aiwg_root=autonomy_env)
    req = AutonomyRequest(request_id="r4", mission_id="M1", requested_scope="ADVISORY_ONLY", requested_action="post", requires_network=True)
    res = contract.evaluate_request(req)
    assert res.decision == "DENY"
    assert "network" in res.reason
