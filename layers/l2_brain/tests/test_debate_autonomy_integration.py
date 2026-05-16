import json
import pytest
from pathlib import Path
from layers.l2_brain.debate_review_runtime import run_debate_review
from layers.l2_brain.mission_autonomy_contract import run_mission_autonomy_contract, evaluate_autonomy_request, AutonomyRequest

def test_debate_autonomy_integration(tmp_path):
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
    
    # 1. Run Debate
    debate = run_debate_review(aiwg_root=aiwg)
    assert debate.decision == "accept_plan"
    
    # 2. Run Autonomy Contract Report
    run_mission_autonomy_contract(aiwg_root=aiwg)
    assert (repo / "mission_autonomy_contract_latest.json").exists()
    
    # 3. Evaluate Safe Request
    safe = evaluate_autonomy_request(AutonomyRequest(
        request_id="safe", mission_id="MISSION_P27", requested_scope="ADVISORY_ONLY", requested_action="test"
    ), aiwg_root=aiwg)
    assert safe.decision == "ALLOW"
    
    # 4. Block on Debate Block
    (repo / "debate_review_latest.json").write_text(json.dumps({"decision": "block"}))
    blocked = evaluate_autonomy_request(AutonomyRequest(
        request_id="blocked", mission_id="MISSION_P27", requested_scope="ADVISORY_ONLY", requested_action="test"
    ), aiwg_root=aiwg)
    assert blocked.decision == "BLOCK"
    assert "debate_block" in blocked.reason
