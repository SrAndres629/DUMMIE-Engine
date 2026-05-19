# Spec Reference: 192_embedding_mesh_foundation
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any
from .contracts import (
    StructuralClass,
    StructuralFinding,
    StructuralTriageReport,
    RiskLevel
)
from .evidence import EvidenceCollector
from .classifier import StructuralClassifier


class StructuralTriageMatrix:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.collector = EvidenceCollector(str(self.repo_root))
        self.classifier = StructuralClassifier(self.collector)

    def analyze(self, base_commit: str = "894978ba00bc6324408fe01d30aa5a620c165dd4") -> StructuralTriageReport:
        index_path = self.repo_root / ".aiwg" / "reports" / "semantic_repo_index_latest.json"
        
        files_data: List[Dict[str, Any]] = []
        if index_path.exists():
            try:
                data = json.loads(index_path.read_text(errors="ignore"))
                # Handle possible schema variants
                if "files" in data:
                    files_data = data["files"]
                elif "summary" in data and "files" in data:
                    files_data = data["files"]
            except Exception:
                pass
                
        findings: List[StructuralFinding] = []
        for file_rec in files_data:
            finding = self.classifier.classify(file_rec)
            findings.append(finding)
            
        # Summary counts
        counts = {cls.value: 0 for cls in StructuralClass}
        for f in findings:
            counts[f.proposed_class.value] = counts.get(f.proposed_class.value, 0) + 1
            
        # Extract top actions (risk-sorted)
        # Risk priority: CRITICAL > HIGH > MEDIUM > LOW
        risk_weights = {
            RiskLevel.CRITICAL.value: 4,
            RiskLevel.HIGH.value: 3,
            RiskLevel.MEDIUM.value: 2,
            RiskLevel.LOW.value: 1
        }
        
        sorted_findings = sorted(
            [f for f in findings if f.risk in [RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM]],
            key=lambda x: (risk_weights.get(x.risk.value, 0), x.path),
            reverse=True
        )
        
        top_actions: List[Dict[str, Any]] = []
        for f in sorted_findings:
            top_actions.append({
                "path": f.path,
                "proposed_class": f.proposed_class.value,
                "risk": f.risk.value,
                "recommendation": f.recommendation.value,
                "reasons": f.reasons
            })
            
        # Health status: FAIL if any high-risk shadow candidate resides in active codebase
        has_shadow_debt = counts.get(StructuralClass.SHADOW_CANDIDATE.value, 0) > 0
        repo_health_status = "FAIL" if has_shadow_debt else "PASS"
        
        return StructuralTriageReport(
            generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            base_commit=base_commit,
            pack_status="triage_completed",
            repo_health_status=repo_health_status,
            files_analyzed=len(findings),
            findings=findings,
            summary_counts=counts,
            top_actions=top_actions,
            limitations=[
                "Deterministic heuristic analysis only. No real embeddings used.",
                "Packaging __init__.py files treated as Active Runtime by design."
            ]
        )
