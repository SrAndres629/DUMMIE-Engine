import json
import pytest
from pathlib import Path
from layers.l2_brain.strategic.strategic_partner_swarm import StrategicPartnerSwarm

@pytest.fixture
def swarm_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    evo = aiwg / "evolution"
    repo = aiwg / "reports"
    evo.mkdir(parents=True)
    repo.mkdir(parents=True)
    
    current = {"current_phase": "P25", "current_block": "test_block"}
    seed = {"next_phase": "P26", "success_conditions": ["Metric 1"]}
    
    (evo / "current_position.json").write_text(json.dumps(current))
    (evo / "next_phase_seed.json").write_text(json.dumps(seed))
    
    return aiwg

def test_swarm_roles_initialization(swarm_env):
    (swarm_env / "reports" / "mission_coherence_guard_latest.json").write_text(json.dumps({"decision": "PASS"}))
    
    swarm = StrategicPartnerSwarm(aiwg_root=swarm_env)
    decision = swarm.run_swarm()
    
    assert decision.swarm_id == "strategic_partner_swarm"
    assert len(decision.roles) == 6
    assert any(r.role == "critic" for r in decision.roles)
    assert decision.decision == "continue_next_phase"

def test_swarm_blocks_on_coherence_failure(swarm_env):
    (swarm_env / "reports" / "mission_coherence_guard_latest.json").write_text(json.dumps({"decision": "FAIL"}))
    
    swarm = StrategicPartnerSwarm(aiwg_root=swarm_env)
    decision = swarm.run_swarm()
    
    assert decision.decision == "block_due_to_coherence_failure"
    critic = next(r for r in decision.roles if r.role == "critic")
    assert critic.decision == "FAIL"

def test_swarm_advisory_policy():
    swarm = StrategicPartnerSwarm()
    # Logic check: should have flags
    assert swarm.aiwg_root.name == ".aiwg"
