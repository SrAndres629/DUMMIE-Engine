from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class WorkstationAction:
    action_id: str
    category: str  # READ_ONLY_STATUS|READ_ONLY_FILE_METADATA|READ_ONLY_REPO_INSPECTION|TEST_COMMAND_RECOMMENDATION|PATCH_PROPOSAL|WORKSPACE_EDIT|TEST_RUN|COMMIT_PUSH|BROWSER_CONTROL|NETWORK_ACTION|CREDENTIAL_ACCESS|ENV_ACCESS|OS_MUTATION|INSTALL_DEPENDENCY|DANGEROUS_OPERATION|UNKNOWN
    requested_action: str
    target_paths: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    requires_workspace_mutation: bool = False
    requires_credentials: bool = False
    requires_network: bool = False


@dataclass
class WorkstationDryRunResult:
    action_id: str
    decision: str  # ALLOW|ALLOW_WITH_HUMAN_APPROVAL|DENY|BLOCK
    category: str
    reason: str = ""
    can_execute_now: bool = False
    requires_authorization: bool = False
    blocked_reasons: list[str] = field(default_factory=list)
    safety_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TrustedWorkstationMode:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"
        self.evolution_root = self.aiwg_root / "evolution"

    def evaluate_action(self, action: WorkstationAction) -> WorkstationDryRunResult:
        # Static Denials
        if action.category in ["CREDENTIAL_ACCESS", "ENV_ACCESS", "BROWSER_CONTROL", "NETWORK_ACTION", "OS_MUTATION", "INSTALL_DEPENDENCY", "DANGEROUS_OPERATION"]:
            return WorkstationDryRunResult(
                action_id=action.action_id,
                decision="BLOCK",
                category=action.category,
                reason=f"policy_violation: category {action.category} is strictly forbidden",
                blocked_reasons=["security_policy_enforcement"]
            )
        
        if action.requires_credentials or action.requires_network:
             return WorkstationDryRunResult(
                action_id=action.action_id,
                decision="BLOCK",
                category=action.category,
                reason="policy_violation: credentials or network access forbidden",
                blocked_reasons=["security_policy_enforcement"]
            )

        # Path-based denials
        for path in action.target_paths:
            if ".env" in path or ".ssh" in path or ".git/config" in path:
                return WorkstationDryRunResult(
                    action_id=action.action_id,
                    decision="BLOCK",
                    category=action.category,
                    reason=f"policy_violation: path {path} is sensitive",
                    blocked_reasons=["sensitive_path_access_denied"]
                )

        # Classification
        safe_categories = ["READ_ONLY_STATUS", "READ_ONLY_FILE_METADATA", "READ_ONLY_REPO_INSPECTION", "TEST_COMMAND_RECOMMENDATION", "PATCH_PROPOSAL"]
        
        if action.category in safe_categories and not action.requires_workspace_mutation:
            return WorkstationDryRunResult(
                action_id=action.action_id,
                decision="ALLOW",
                category=action.category,
                reason="safe_read_only_or_advisory_category",
                can_execute_now=True
            )
        
        if action.requires_workspace_mutation or action.category in ["WORKSPACE_EDIT", "TEST_RUN", "COMMIT_PUSH"]:
            return WorkstationDryRunResult(
                action_id=action.action_id,
                decision="ALLOW_WITH_HUMAN_APPROVAL",
                category=action.category,
                reason="workspace_mutation_requires_manual_authorization",
                requires_authorization=True
            )

        return WorkstationDryRunResult(
            action_id=action.action_id,
            decision="DENY",
            category=action.category,
            reason="unknown_or_unclassified_action_risk"
        )

    def run_mode_report(self) -> dict[str, Any]:
        samples = [
            WorkstationAction("s1", "READ_ONLY_STATUS", "git status"),
            WorkstationAction("s2", "PATCH_PROPOSAL", "suggest code change"),
            WorkstationAction("s3", "WORKSPACE_EDIT", "write file", requires_workspace_mutation=True),
            WorkstationAction("s4", "ENV_ACCESS", "read .env", target_paths=[".env"]),
            WorkstationAction("s5", "BROWSER_CONTROL", "open google"),
            WorkstationAction("s6", "INSTALL_DEPENDENCY", "npm install"),
        ]
        
        evaluations = [self.evaluate_action(s).to_dict() for s in samples]
        
        report = {
            "mode_id": "trusted_workstation_mode",
            "phase": "P29",
            "decision": "PASS",
            "dry_run_only": True,
            "actual_execution_enabled": False,
            "policy": {
                "safe_read_only_allowed": True,
                "workspace_mutation_requires_authorization": True,
                "credentials_access_denied": True,
                "env_access_denied": True,
                "browser_control_denied_by_default": True,
                "network_action_denied_by_default": True,
                "install_dependency_denied_by_default": True
            },
            "sample_evaluations": evaluations,
            "evidence_refs": [".aiwg/reports/mission_autonomy_contract_latest.json"],
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        }

        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "trusted_workstation_mode_latest.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        return report


def evaluate_workstation_action(action: WorkstationAction, aiwg_root: str | Path = ".aiwg") -> WorkstationDryRunResult:
    return TrustedWorkstationMode(aiwg_root=aiwg_root).evaluate_action(action)


def run_trusted_workstation_mode(aiwg_root: str | Path = ".aiwg") -> dict[str, Any]:
    # In P29, this just runs the evaluation logic and reports
    mode = TrustedWorkstationMode(aiwg_root=aiwg_root)
    return mode.run_mode_report()
