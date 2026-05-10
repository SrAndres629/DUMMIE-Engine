import pytest
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


@pytest.fixture
def store():
    return MockSessionStore()


@pytest.fixture
def manager(store):
    return PatchTransactionManager(store)


@pytest.fixture
def base_proposal():
    return PatchProposal(
        proposal_id="prop-1",
        source_pattern_id="pat-1",
        mission_id="miss-1",
        affected_paths=["src/main.py"],
        diff_unified="+ code",
        tests_to_run=["pytest"],
        rollback_plan="reset",
        safety_gates={
            "apply_patch_enabled": True,
            "persona_guardian_required": True,
            "persona_guardian_approved": True,
            "coldplanner_selected_action": True
        }
    )


def test_creates_transaction_artifact(manager, store, base_proposal):
    txn = manager.create_transaction("sess-1", base_proposal)
    assert txn.status == "AWAITING_APPROVAL"
    assert len(store.events) == 1
    assert store.events[0]["type"] == "TRANSACTION_CREATED"
    assert store.events[0]["data"]["status"] == "AWAITING_APPROVAL"
    
    artifact_name = store.events[0]["refs"][0]
    assert artifact_name in store.artifacts


def test_blocks_env_file(manager, store, base_proposal):
    base_proposal.affected_paths = [".env"]
    txn = manager.create_transaction("sess-1", base_proposal)
    assert txn.status == "BLOCKED"
    assert any(".env" in err for err in txn.validation_errors)


def test_allows_creation_when_apply_patch_disabled(manager, base_proposal):
    # FIXED: This should now return AWAITING_APPROVAL, not BLOCKED
    base_proposal.safety_gates["apply_patch_enabled"] = False
    txn = manager.create_transaction("sess-1", base_proposal)
    assert txn.status == "AWAITING_APPROVAL"


def test_blocks_missing_persona_approval(manager, base_proposal):
    base_proposal.safety_gates["persona_guardian_approved"] = False
    txn = manager.create_transaction("sess-1", base_proposal)
    assert txn.status == "BLOCKED"
    assert any("PersonaGuardian" in err for err in txn.validation_errors)


def test_blocks_missing_tests(manager, base_proposal):
    # FIXED: Remove dummy check
    base_proposal.tests_to_run = []
    txn = manager.create_transaction("sess-1", base_proposal)
    assert txn.status == "BLOCKED"
    assert any("tests_to_run" in err for err in txn.validation_errors)


def test_blocks_missing_rollback(manager, base_proposal):
    base_proposal.rollback_plan = ""
    txn = manager.create_transaction("sess-1", base_proposal)
    assert txn.status == "BLOCKED"
    assert any("rollback_plan" in err for err in txn.validation_errors)
