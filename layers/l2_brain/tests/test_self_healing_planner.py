import pytest
from self_healing_planner import SelfHealingPlanner
from patch_transaction import PatchProposal

class MockGateway:
    pass

@pytest.mark.asyncio
async def test_planner_generates_typed_proposal_from_mission():
    planner = SelfHealingPlanner(MockGateway())
    mission = {
        "mission_id": "miss-123",
        "source_pattern_id": "pattern-456",
        "goal": "Fix semantic decay",
        "context_refs": ["src/logic.py"],
        "self_healing_safety_gates": {
            "apply_patch_enabled": False,
            "persona_guardian_required": True
        }
    }
    
    proposal = await planner.generate_patch_proposal(mission)
    
    assert isinstance(proposal, PatchProposal)
    assert proposal.mission_id == "miss-123"
    assert proposal.source_pattern_id == "pattern-456"
    assert "src/logic.py" in proposal.affected_paths
    assert proposal.tests_to_run
    assert proposal.rollback_plan
    assert proposal.safety_gates["apply_patch_enabled"] is False
