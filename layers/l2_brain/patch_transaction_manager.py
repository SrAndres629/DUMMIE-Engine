import json
import uuid
from typing import Any, List

from patch_transaction import PatchProposal, PatchTransaction

BLOCKED_PATHS = {".env", ".git", "poetry.lock", "pyproject.toml", "Cargo.lock"}


class PatchTransactionManager:
    """
    Orchestrates the lifecycle of self-healing patches.
    MVP: Dry-run only. Never applies physical patches.
    """
    def __init__(self, session_store: Any):
        self.session_store = session_store

    def create_transaction(self, session_id: str, proposal: PatchProposal) -> PatchTransaction:
        # Validate blocked paths
        for path in proposal.affected_paths:
            if any(path.endswith(b) or b in path.split("/") for b in BLOCKED_PATHS):
                txn = self._build_blocked_transaction(proposal, f"Path blocked by security policy: {path}")
                self._record_transaction(session_id, txn)
                return txn

        # Validate gates
        gates = proposal.safety_gates or {}
        if not gates.get("apply_patch_enabled"):
            txn = self._build_blocked_transaction(proposal, "Direct apply is disabled (apply_patch_enabled=False)")
            self._record_transaction(session_id, txn)
            return txn
            
        if gates.get("persona_guardian_required") and not gates.get("persona_guardian_approved"):
            txn = self._build_blocked_transaction(proposal, "PersonaGuardian approval required but missing")
            self._record_transaction(session_id, txn)
            return txn

        if not gates.get("coldplanner_selected_action"):
            txn = self._build_blocked_transaction(proposal, "ColdPlanner did not explicitly select this action")
            self._record_transaction(session_id, txn)
            return txn

        # Success - create awaiting approval transaction
        txn_id = f"txn-{uuid.uuid4().hex[:8]}"
        branch_name = f"heal-{proposal.proposal_id[:8]}"
        
        txn = PatchTransaction.from_proposal(
            transaction_id=txn_id,
            branch_name=branch_name,
            proposal=proposal
        )
        txn.status = "AWAITING_APPROVAL"
        
        self._record_transaction(session_id, txn)
        return txn

    def _build_blocked_transaction(self, proposal: PatchProposal, reason: str) -> PatchTransaction:
        txn_id = f"txn-{uuid.uuid4().hex[:8]}"
        branch_name = f"heal-blocked-{proposal.proposal_id[:8]}"
        try:
            txn = PatchTransaction.from_proposal(
                transaction_id=txn_id,
                branch_name=branch_name,
                proposal=proposal
            )
            txn.status = "BLOCKED"
            txn.evidence_refs = [f"block_reason:{reason}"]
        except ValueError:
            # If proposal is fundamentally broken (e.g. no tests), still return blocked struct
            txn = PatchTransaction(
                transaction_id=txn_id,
                source_pattern_id=proposal.source_pattern_id,
                mission_id=proposal.mission_id,
                proposal_id=proposal.proposal_id,
                branch_name=branch_name,
                affected_paths=proposal.affected_paths,
                diff_unified=proposal.diff_unified,
                tests_to_run=proposal.tests_to_run or ["dummy"],
                rollback_plan=proposal.rollback_plan or "dummy",
                evidence_refs=[f"block_reason:{reason}"],
                safety_gates=proposal.safety_gates,
                status="BLOCKED"
            )
        return txn

    def _record_transaction(self, session_id: str, txn: PatchTransaction) -> None:
        if not self.session_store:
            return
            
        artifact_name = f"transaction_{txn.transaction_id}.json"
        self.session_store.save_artifact(
            session_id=session_id,
            artifact_name=artifact_name,
            content=json.dumps(txn.to_dict(), indent=2)
        )
        
        self.session_store.append_event(
            session_id=session_id,
            event_type="TRANSACTION_CREATED",
            summary=f"PatchTransaction {txn.status}: {len(txn.affected_paths)} files",
            data={"transaction_id": txn.transaction_id, "status": txn.status},
            evidence_refs=[artifact_name]
        )
