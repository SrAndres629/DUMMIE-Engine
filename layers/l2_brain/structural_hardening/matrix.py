from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from .classifier import StructuralClassifier
from .contracts import Recommendation, RiskLevel, StructuralFinding, StructuralTriageReport
from .evidence import EvidenceCollector


class StructuralTriageMatrix:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.classifier = StructuralClassifier()

    def build(
        self,
        semantic_index: Dict[str, Any],
        semantic_matrix: Dict[str, Any],
        max_actions: int = 50,
        include_low_risk: bool = False,
    ) -> StructuralTriageReport:
        files = _safe_files_from_index(semantic_index)
        collector = EvidenceCollector(self.repo_root, semantic_index, semantic_matrix)

        findings: List[StructuralFinding] = []
        for file_rec in files:
            path = file_rec.get("path")
            if not path:
                continue
            evidence = collector.collect(path)
            finding = self.classifier.classify(file_rec, evidence)
            findings.append(finding)

        by_class = Counter(f.proposed_class.value for f in findings)
        by_risk = Counter(f.risk.value for f in findings)
        by_recommendation = Counter(f.recommendation.value for f in findings)
        pack_status = "PASS_WITH_WARNINGS"
        if not findings:
            pack_status = "FAIL"

        debt_indicators = (
            by_class.get("SHADOW_CANDIDATE", 0)
            + by_class.get("ORPHAN_TEST_CANDIDATE", 0)
            + by_class.get("UNKNOWN", 0)
            + by_risk.get(RiskLevel.MEDIUM.value, 0)
            + by_risk.get(RiskLevel.HIGH.value, 0)
            + by_risk.get(RiskLevel.CRITICAL.value, 0)
        )
        repo_health_status = "FAIL" if debt_indicators > 0 else "PASS"

        top_actions = _select_top_actions(findings, max_actions=max_actions, include_low_risk=include_low_risk)

        # Compile binding registry counts
        from .bindings import ContractBindingRegistry, BindingStatus
        registry = ContractBindingRegistry()
        all_bindings = registry.get_all_bindings()
        bound_runtime = sum(1 for b in all_bindings if b.binding_status == BindingStatus.BOUND_ACTIVE_RUNTIME)
        needs_manual = sum(1 for b in all_bindings if b.binding_status == BindingStatus.NEEDS_MANUAL_OWNER)
        deferred = sum(1 for b in all_bindings if b.binding_status == BindingStatus.DEFERRED_NO_SAFE_ACTION)

        summary_counts = {
            "by_class": dict(sorted(by_class.items())),
            "by_risk": dict(sorted(by_risk.items())),
            "by_recommendation": dict(sorted(by_recommendation.items())),
            "bindings_summary": {
                "bound_active_runtime": bound_runtime,
                "needs_manual_owner": needs_manual,
                "deferred_no_safe_action": deferred,
            }
        }


        report = StructuralTriageReport(
            generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            base_commit=_git_head(self.repo_root),
            pack_name="Structural Hardening Pack 2 - Contract-First Triage",
            pack_status=pack_status,
            repo_health_status=repo_health_status,
            files_analyzed=len(findings),
            findings=findings,
            summary_counts=summary_counts,
            top_actions=top_actions,
            limitations=[
                "Deterministic evidence only; no embedding or ML-based reasoning used.",
                "No physical file moves/deletes performed in this phase.",
                "Classification depends on currently indexed artifacts and deterministic references.",
            ],
            next_recommended_phase="Structural Hardening Pack 2.1 - targeted contract binding and safe physical changes",
        )
        return report


def load_json_safe(path: Path, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
    fallback: Dict[str, Any] = default or {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
        return fallback
    except Exception:
        return fallback


def _safe_files_from_index(semantic_index: Dict[str, Any]) -> List[Dict[str, Any]]:
    if isinstance(semantic_index.get("files"), list):
        return semantic_index["files"]

    nested = semantic_index.get("semantic_repo_index")
    if isinstance(nested, dict) and isinstance(nested.get("files"), list):
        return nested["files"]

    return []


def _select_top_actions(
    findings: List[StructuralFinding],
    max_actions: int,
    include_low_risk: bool,
) -> List[StructuralFinding]:
    filtered = [
        f
        for f in findings
        if f.recommendation != Recommendation.NO_ACTION
        and (include_low_risk or f.risk in {RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM})
    ]
    rank = {RiskLevel.CRITICAL: 0, RiskLevel.HIGH: 1, RiskLevel.MEDIUM: 2, RiskLevel.LOW: 3}
    filtered.sort(key=lambda f: (rank.get(f.risk, 4), -f.confidence, f.path))
    return filtered[:max_actions]


def _git_head(repo_root: Path) -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN"
