from __future__ import annotations

# Spec: 129_mission_autonomy_contract

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class AutonomyRequest:
    request_id: str
    mission_id: str
    requested_scope: str  # ADVISORY_ONLY|ANALYZE_PLAN|SPEC_AUTHORING|PATCH_PROPOSAL|WORKSPACE_WRITE|TEST_EXECUTION|COMMIT_PUSH|TRUSTED_WORKSTATION_REQUIRED|DENIED
    requested_action: str
    target_paths: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    risk_level: str = "low"  # low|medium|high|critical
    requires_workspace_mutation: bool = False
    requires_external_action: bool = False
    requires_credentials: bool = False
    requires_network: bool = False


@dataclass
class AutonomyDecision:
    request_id: str
    decision: str  # ALLOW|ALLOW_WITH_VERIFICATION|ALLOW_WITH_HUMAN_APPROVAL|DENY|BLOCK|DEFER_TO_P29
    granted_scope: str
    reason: str = ""
    required_authorizations: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    expires_after_phase: str = ""
    can_execute_now: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MissionAutonomyContract:
    OBSOLETE_SCOPES = {"READ_ONLY_ANALYSIS"}
    COGNITIVE_SCOPES = {"ADVISORY_ONLY", "ANALYZE_PLAN", "SPEC_AUTHORING", "TEST_COMMAND_RECOMMENDATION", "PATCH_PROPOSAL"}
    VERIFIED_MUTATION_SCOPES = {"WORKSPACE_WRITE", "TEST_EXECUTION", "COMMIT_PUSH"}

    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"
        self.evolution_root = self.aiwg_root / "evolution"

    def evaluate_request(self, request: AutonomyRequest) -> AutonomyDecision:
        # Load context
        current_pos = self._load_json(self.evolution_root / "current_position.json")
        debate = self._load_json(self.reports_root / "debate_review_latest.json")
        
        decision = "DENY"
        granted_scope = "DENIED"
        reason = ""
        auths = []
        blocked = []
        can_exec = False

        # Static Denials
        if request.requires_credentials or ".env" in str(request.target_paths):
            return AutonomyDecision(
                request_id=request.request_id,
                decision="BLOCK",
                granted_scope="DENIED",
                reason="policy_violation: credentials/env access strictly forbidden",
                blocked_reasons=["security_policy_breach"]
            )
        
        if request.requires_network or request.requires_external_action:
            return AutonomyDecision(
                request_id=request.request_id,
                decision="DENY",
                granted_scope="DENIED",
                reason="policy_violation: external/network actions forbidden in P28",
                blocked_reasons=["p28_offline_only_constraint"]
            )

        # Authority Gates
        if debate.get("decision") == "block":
            return AutonomyDecision(
                request_id=request.request_id,
                decision="BLOCK",
                granted_scope="DENIED",
                reason="debate_block: adversarial review blocked the mission",
                blocked_reasons=["adversarial_review_veto"]
            )

        # Scope Evaluation
        if request.requested_scope in self.OBSOLETE_SCOPES:
            decision = "DENY"
            granted_scope = "DENIED"
            reason = f"obsolete_scope: {request.requested_scope} has been replaced by ANALYZE_PLAN"
        elif request.requested_scope in self.COGNITIVE_SCOPES and not request.requires_workspace_mutation:
            decision = "ALLOW"
            granted_scope = request.requested_scope
            can_exec = True
            reason = "active_cognitive_scope"
        elif request.requested_scope in self.VERIFIED_MUTATION_SCOPES or request.requires_workspace_mutation:
            if request.evidence_refs:
                decision = "ALLOW_WITH_VERIFICATION"
                granted_scope = request.requested_scope
                auths.append("verification_required")
                can_exec = True
                reason = "workspace_mutation_allowed_with_verification_evidence"
            else:
                decision = "ALLOW_WITH_HUMAN_APPROVAL"
                granted_scope = request.requested_scope
                auths.append("human_approval")
                reason = "workspace_mutation_requires_evidence_or_manual_authorization"
        elif "HUMAN_APPROVED" in request.requested_scope:
            decision = "ALLOW_WITH_HUMAN_APPROVAL"
            granted_scope = request.requested_scope
            auths.append("human_approval")
            reason = "workspace_mutation_requires_manual_authorization"
        elif "TRUSTED_WORKSTATION" in request.requested_scope:
            decision = "DEFER_TO_P29"
            granted_scope = "DENIED"
            reason = "workstation_mode_not_implemented_until_p29"
        
        return AutonomyDecision(
            request_id=request.request_id,
            decision=decision,
            granted_scope=granted_scope,
            reason=reason,
            required_authorizations=auths,
            blocked_reasons=blocked,
            can_execute_now=can_exec,
            evidence_refs=[".aiwg/reports/debate_review_latest.json"]
        )

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}


class MissionAutonomyRuntime:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"
        self.evolution_root = self.aiwg_root / "evolution"

    def run_contract_demo(self) -> dict[str, Any]:
        current_pos = self._load_json(self.evolution_root / "current_position.json")
        next_seed = self._load_json(self.evolution_root / "next_phase_seed.json")
        
        contract = MissionAutonomyContract(aiwg_root=self.aiwg_root)
        
        policy = {
            "read_only_default_obsolete": True,
            "active_cognitive_default": "ANALYZE_PLAN",
            "workspace_mutation_requires_authorization": True,
            "workspace_mutation_with_evidence_enabled": True,
            "trusted_workstation_deferred_to_p29": True,
            "credentials_access_denied": True,
            "external_actions_denied_by_default": True
        }
        
        # Sample decision for reporting
        sample = contract.evaluate_request(AutonomyRequest(
            request_id="p28-init-check",
            mission_id=f"MISSION_{next_seed.get('next_phase')}",
            requested_scope="ANALYZE_PLAN",
            requested_action="validate_contract_boot",
            risk_level="low"
        ))

        report = {
            "contract_id": "mission_autonomy_contract",
            "phase": "P28",
            "mission_id": f"MISSION_{next_seed.get('next_phase')}",
            "decision": "PASS",
            "default_allowed_scopes": ["ANALYZE_PLAN", "SPEC_AUTHORING", "PATCH_PROPOSAL"],
            "verified_mutation_scopes": ["WORKSPACE_WRITE", "TEST_EXECUTION", "COMMIT_PUSH"],
            "obsolete_scopes": ["READ_ONLY_ANALYSIS"],
            "restricted_scopes": ["TRUSTED_WORKSTATION_REQUIRED"],
            "sample_decisions": [sample.to_dict()],
            "policy": policy,
            "evidence_refs": [".aiwg/reports/debate_review_latest.json"],
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        }

        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "mission_autonomy_contract_latest.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        return report

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}


def evaluate_autonomy_request(request: AutonomyRequest, aiwg_root: str | Path = ".aiwg") -> AutonomyDecision:
    return MissionAutonomyContract(aiwg_root=aiwg_root).evaluate_request(request)


def run_mission_autonomy_contract(aiwg_root: str | Path = ".aiwg") -> dict[str, Any]:
    return MissionAutonomyRuntime(aiwg_root=aiwg_root).run_contract_demo()
