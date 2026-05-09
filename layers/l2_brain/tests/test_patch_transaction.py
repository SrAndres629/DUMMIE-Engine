import pytest
from patch_transaction import PatchProposal, PatchTransaction


def test_creates_transaction_from_proposal_without_strict_enforcement():
    """
    Validation is now handled by the Manager to allow BLOCKED status artifacts.
    """
    proposal = PatchProposal(
        proposal_id="prop-1",
        source_pattern_id="pat-1",
        mission_id="miss-1",
        affected_paths=["main.py"],
        diff_unified="--- main.py\n+++ main.py\n+ print('hello')",
        tests_to_run=["pytest test_main.py"],
        rollback_plan="git checkout main.py",
        safety_gates={"apply_patch_enabled": False}
    )

    txn = PatchTransaction.from_proposal(
        transaction_id="txn-1",
        branch_name="heal-prop-1",
        proposal=proposal,
        evidence_refs=["ev-1"]
    )

    assert txn.transaction_id == "txn-1"
    assert txn.source_pattern_id == "pat-1"
    assert txn.status == "CREATED"
    assert "main.py" in txn.affected_paths


def test_serializes_to_json_dict():
    proposal = PatchProposal(
        proposal_id="prop-1",
        source_pattern_id="pat-1",
        mission_id="miss-1",
        affected_paths=[],
        diff_unified="",
        tests_to_run=["pytest"],
        rollback_plan="reset",
    )
    txn = PatchTransaction.from_proposal("txn-1", "branch", proposal)
    
    d = txn.to_dict()
    assert d["transaction_id"] == "txn-1"
    assert d["status"] == "CREATED"
    assert d["source_pattern_id"] == "pat-1"
    assert "validation_errors" in d
