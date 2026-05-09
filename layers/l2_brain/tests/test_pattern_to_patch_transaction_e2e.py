import pytest
import asyncio
from prompt_to_mission import PromptToMissionCompiler
from self_healing_planner import SelfHealingPlanner
from patch_transaction_manager import PatchTransactionManager
from patch_transaction import PatchProposal


class MockSessionStore:
    def __init__(self):
        self.artifacts = {}
        self.events = []

    def save_artifact(self, session_id, artifact_name, content):
        self.artifacts[artifact_name] = content

    def append_event(self, session_id, event_type, summary, data, evidence_refs):
        self.events.append({
            "type": event_type,
            "data": data,
            "refs": evidence_refs
        })


class MockGateway:
    pass


@pytest.mark.asyncio
async def test_pattern_to_patch_transaction_e2e_successful_dry_run():
    # 1. Synthetic semantic decay pattern
    pattern = {
        "pattern_id": "decay_123",
        "name": "Semantic decay",
        "hypothesis": "File diverges from spec",
        "proposed_rule": "Add tests",
        "recommended_action": "REPAIR_SEMANTIC_DECAY",
        "coldplanner_metrics": {"risk": 0.3}
    }

    # 2. Compile mission
    compiler = PromptToMissionCompiler()
    mission = compiler.compile_from_pattern(pattern)
    assert mission["self_healing_safety_gates"]["apply_patch_enabled"] is False

    # 3. Planner proposes patch
    planner = SelfHealingPlanner(MockGateway())
    proposal = await planner.generate_patch_proposal(mission)
    
    # Simulate PersonaGuardian and ColdPlanner approving
    proposal.safety_gates["persona_guardian_approved"] = True
    proposal.safety_gates["coldplanner_selected_action"] = True

    # 4. Patch Transaction Manager
    store = MockSessionStore()
    manager = PatchTransactionManager(store)
    
    # 5. Assertions
    # FIXED: apply_patch_enabled=False should result in AWAITING_APPROVAL now
    txn = manager.create_transaction("sess-1", proposal)
    assert txn.status == "AWAITING_APPROVAL"
    assert len(store.events) == 1
    
    # Validate JSON serialization
    serialized = txn.to_dict()
    assert serialized["transaction_id"] == txn.transaction_id
    assert "apply_patch_enabled" in serialized["safety_gates"]


@pytest.mark.asyncio
async def test_pattern_to_patch_transaction_e2e_blocked_path():
    pattern = {
        "pattern_id": "decay_env",
        "name": "Semantic decay",
        "hypothesis": ".env is wrong",
        "proposed_rule": "Fix .env",
        "recommended_action": "REPAIR_SEMANTIC_DECAY"
    }

    compiler = PromptToMissionCompiler()
    mission = compiler.compile_from_pattern(pattern)

    planner = SelfHealingPlanner(MockGateway())
    proposal = await planner.generate_patch_proposal(mission)
    
    # Force a blocked path
    proposal.affected_paths = [".env"]
    
    # Even if we bypass gates, the path blocker must trigger
    proposal.safety_gates["apply_patch_enabled"] = True
    proposal.safety_gates["persona_guardian_approved"] = True
    proposal.safety_gates["coldplanner_selected_action"] = True

    store = MockSessionStore()
    manager = PatchTransactionManager(store)
    
    txn = manager.create_transaction("sess-1", proposal)
    
    assert txn.status == "BLOCKED"
    assert any(".env" in err for err in txn.validation_errors)
