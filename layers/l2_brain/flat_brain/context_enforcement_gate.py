from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ContextEnforcementDecision:
    request_id: str
    decision: str  # ALLOW_MANIFEST_ONLY|ALLOW_DOSSIER_CONTEXT|ALLOW_SELECTED_FILE_READ|BLOCK_RAW_FOLDER_BULK_LOAD|REQUIRE_REPO_INTELLIGENCE_REFRESH
    reason: str
    recommended_strategy: str
    risk_score: float
    evidence_refs: list[str] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ContextEnforcementGate:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.intel_root = self.aiwg_root / "repo_intelligence"
        self.reports_root = self.aiwg_root / "reports"

    def evaluate_context_request(self, request: dict[str, Any]) -> ContextEnforcementDecision:
        user_intent = request.get("user_intent", "unknown")
        task_type = request.get("task_type", "unknown")
        requested_paths = request.get("requested_paths", [])
        
        manifest_path = self.intel_root / "repo_intelligence_manifest.json"
        if not manifest_path.exists():
            return ContextEnforcementDecision(
                request_id=request.get("request_id", "req_unknown"),
                decision="REQUIRE_REPO_INTELLIGENCE_REFRESH",
                reason="Repo intelligence manifest is missing.",
                recommended_strategy="Run repo-intelligence command first.",
                risk_score=1.0,
                generated_at=self._utc_now()
            )

        # Policy: BLOCK_RAW_FOLDER_BULK_LOAD
        if request.get("requires_full_repo_scan") and task_type != "repo_intelligence_refresh":
            return ContextEnforcementDecision(
                request_id=request.get("request_id", "req_unknown"),
                decision="BLOCK_RAW_FOLDER_BULK_LOAD",
                reason="Direct raw folder scans are blocked to prevent context waste.",
                recommended_strategy="Use repo-intelligence manifests or dossiers.",
                risk_score=0.9,
                evidence_refs=[str(manifest_path)],
                generated_at=self._utc_now()
            )

        # Policy: Prefer dossiers for analysis/planning
        if task_type in ["analysis", "planning"] and not request.get("requires_code_read"):
            return ContextEnforcementDecision(
                request_id=request.get("request_id", "req_unknown"),
                decision="ALLOW_DOSSIER_CONTEXT",
                reason="Task type allows dossier-only context.",
                recommended_strategy="Load relevant folder and file dossiers.",
                risk_score=0.1,
                evidence_refs=[str(self.reports_root / "folder_dossier_index.json")],
                generated_at=self._utc_now()
            )

        # Policy: ALLOW_SELECTED_FILE_READ for implementation/debugging
        if task_type in ["implementation", "debugging"] or request.get("requires_code_read"):
            return ContextEnforcementDecision(
                request_id=request.get("request_id", "req_unknown"),
                decision="ALLOW_SELECTED_FILE_READ",
                reason="Implementation/debugging tasks require physical file reads.",
                recommended_strategy="Read specific files, but keep dossiers for overview.",
                risk_score=0.4,
                evidence_refs=requested_paths,
                generated_at=self._utc_now()
            )

        return ContextEnforcementDecision(
            request_id=request.get("request_id", "req_unknown"),
            decision="ALLOW_MANIFEST_ONLY",
            reason="Defaulting to manifest-only context for unknown task types.",
            recommended_strategy="Load repo_intelligence_manifest.json.",
            risk_score=0.2,
            generated_at=self._utc_now()
        )

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_context_enforcement_gate(request: dict[str, Any], aiwg_root: str | Path = ".aiwg") -> ContextEnforcementDecision:
    gate = ContextEnforcementGate(aiwg_root=aiwg_root)
    decision = gate.evaluate_context_request(request)
    
    reports_dir = Path(aiwg_root) / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "context_enforcement_gate_latest.json").write_text(
        json.dumps(decision.to_dict(), indent=2) + "\n", encoding="utf-8"
    )
    
    return decision
