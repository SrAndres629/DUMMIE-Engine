from dataclasses import dataclass, field
from typing import Literal, Any, Dict, List


@dataclass
class PatchProposal:
    proposal_id: str
    source_pattern_id: str
    mission_id: str
    affected_paths: List[str]
    diff_unified: str
    tests_to_run: List[str]
    rollback_plan: str
    safety_gates: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PatchTransaction:
    transaction_id: str
    source_pattern_id: str
    mission_id: str
    proposal_id: str
    branch_name: str
    affected_paths: List[str]
    diff_unified: str
    tests_to_run: List[str]
    rollback_plan: str
    evidence_refs: List[str]
    safety_gates: Dict[str, Any]
    status: Literal[
        "CREATED",
        "DRY_RUN_OK",
        "DRY_RUN_FAILED",
        "VALIDATION_RUNNING",
        "VALIDATION_PASSED",
        "VALIDATION_FAILED",
        "AWAITING_APPROVAL",
        "APPLIED",
        "ROLLED_BACK",
        "BLOCKED",
    ] = "CREATED"
    validation_errors: List[str] = field(default_factory=list)

    @classmethod
    def from_proposal(
        cls,
        transaction_id: str,
        branch_name: str,
        proposal: PatchProposal,
        evidence_refs: List[str] = None
    ) -> "PatchTransaction":
        # Validation is now delegated to the Manager to allow BLOCKED state with errors
        return cls(
            transaction_id=transaction_id,
            source_pattern_id=proposal.source_pattern_id,
            mission_id=proposal.mission_id,
            proposal_id=proposal.proposal_id,
            branch_name=branch_name,
            affected_paths=list(proposal.affected_paths),
            diff_unified=proposal.diff_unified,
            tests_to_run=list(proposal.tests_to_run),
            rollback_plan=proposal.rollback_plan,
            evidence_refs=evidence_refs or [],
            safety_gates=dict(proposal.safety_gates),
            status="CREATED"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "source_pattern_id": self.source_pattern_id,
            "mission_id": self.mission_id,
            "proposal_id": self.proposal_id,
            "branch_name": self.branch_name,
            "affected_paths": self.affected_paths,
            "diff_unified": self.diff_unified,
            "tests_to_run": self.tests_to_run,
            "rollback_plan": self.rollback_plan,
            "evidence_refs": self.evidence_refs,
            "safety_gates": self.safety_gates,
            "status": self.status,
            "validation_errors": self.validation_errors,
        }
