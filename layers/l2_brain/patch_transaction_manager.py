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
        validation_errors = []

        # 1. Structural Validations (These lead to BLOCKED)
        for path in proposal.affected_paths:
            if any(path.endswith(b) or b in path.split("/") for b in BLOCKED_PATHS):
                validation_errors.append(f"Path blocked by security policy: {path}")

        if not proposal.tests_to_run:
            validation_errors.append("Proposal lacks tests_to_run")
            
        if not proposal.rollback_plan or not proposal.rollback_plan.strip():
            validation_errors.append("Proposal lacks a valid rollback_plan")

        # 2. Semantic Gates (Some might block, others just force AWAITING_APPROVAL)
        gates = proposal.safety_gates or {}
        
        # Missing approvals block the transaction
        if gates.get("persona_guardian_required") and not gates.get("persona_guardian_approved"):
            validation_errors.append("PersonaGuardian approval required but missing")

        if not gates.get("coldplanner_selected_action"):
            validation_errors.append("ColdPlanner did not explicitly select this action")

        # If we have structural/approval errors, it's BLOCKED
        if validation_errors:
            txn = self._build_blocked_transaction(proposal, validation_errors)
            self._record_transaction(session_id, txn)
            return txn

        # 3. Success (AWAITING_APPROVAL)
        # Note: apply_patch_enabled=False no longer blocks creation.
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

    def _build_blocked_transaction(self, proposal: PatchProposal, errors: List[str]) -> PatchTransaction:
        txn_id = f"txn-{uuid.uuid4().hex[:8]}"
        branch_name = f"heal-blocked-{proposal.proposal_id[:8]}"
        
        txn = PatchTransaction.from_proposal(
            transaction_id=txn_id,
            branch_name=branch_name,
            proposal=proposal
        )
        txn.status = "BLOCKED"
        txn.validation_errors = errors
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
