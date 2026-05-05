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

    # 3. Planner proposes patch (simulated)
    planner = SelfHealingPlanner(MockGateway())
    proposal_dict = await planner.generate_patch_proposal(mission)
    
    # Enrich the proposal with test-specific data to pass the schema
    proposal = PatchProposal(
        proposal_id=proposal_dict["mission_id"] or "prop-1",
        source_pattern_id=mission["source_pattern_id"],
        mission_id=mission["mission_id"],
        affected_paths=["src/decayed.py"],
        diff_unified="+ def new_test(): pass",
        tests_to_run=["pytest tests/test_decayed.py"],
        rollback_plan="git checkout src/decayed.py",
        safety_gates=mission["self_healing_safety_gates"]
    )
    
    # Simulate PersonaGuardian and ColdPlanner approving
    proposal.safety_gates["persona_guardian_approved"] = True
    proposal.safety_gates["coldplanner_selected_action"] = True

    # 4. Patch Transaction Manager
    store = MockSessionStore()
    manager = PatchTransactionManager(store)
    
    txn = manager.create_transaction("sess-1", proposal)
    
    # 5. Assertions
    assert txn.status == "BLOCKED" # Wait, apply_patch_enabled is False!
    assert "apply_patch_enabled" in txn.evidence_refs[0]
    
    # Let's test the successful case by overriding the gate locally for the test
    proposal.safety_gates["apply_patch_enabled"] = True
    txn_success = manager.create_transaction("sess-1", proposal)
    
    assert txn_success.status == "AWAITING_APPROVAL"
    assert len(store.events) == 2
    assert store.events[1]["type"] == "TRANSACTION_CREATED"
    
    # Validate JSON serialization
    serialized = txn_success.to_dict()
    assert serialized["transaction_id"] == txn_success.transaction_id


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
    proposal_dict = await planner.generate_patch_proposal(mission)
    
    proposal = PatchProposal(
        proposal_id="prop-env",
        source_pattern_id=mission["source_pattern_id"],
        mission_id=mission["mission_id"],
        affected_paths=[".env"],
        diff_unified="+ SECRET=123",
        tests_to_run=["pytest"],
        rollback_plan="git checkout .env",
        safety_gates=mission["self_healing_safety_gates"]
    )
    
    # Even if we bypass gates, the path blocker must trigger
    proposal.safety_gates["apply_patch_enabled"] = True
    proposal.safety_gates["persona_guardian_approved"] = True
    proposal.safety_gates["coldplanner_selected_action"] = True

    store = MockSessionStore()
    manager = PatchTransactionManager(store)
    
    txn = manager.create_transaction("sess-1", proposal)
    
    assert txn.status == "BLOCKED"
    assert "Path blocked" in txn.evidence_refs[0]
    assert ".env" in txn.evidence_refs[0]
