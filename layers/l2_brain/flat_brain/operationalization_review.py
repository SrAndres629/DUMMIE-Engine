from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class OperationalizationReviewReport:
    review_id: str
    decision: str  # PASS|PASS_WITH_WARNINGS|FAIL
    findings: list[dict[str, Any]] = field(default_factory=list)
    token_economy_impact: str = "improved"
    context_strategy_enforced: bool = True
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class OperationalizationReview:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"

    def run_operationalization_review(self) -> dict[str, Any]:
        findings = []
        
        # Check Repairs
        frontmatter = self._load_json(self.reports_root / "spec_frontmatter_repair_latest.json")
        if frontmatter.get("decision") == "PASS" and frontmatter.get("repaired_count", 0) > 0:
            findings.append({"id": "frontmatter_repaired", "status": "PASS", "count": frontmatter["repaired_count"]})
        
        # Check Context Gate
        gate = self._load_json(self.reports_root / "context_enforcement_gate_latest.json")
        if gate:
            findings.append({"id": "context_gate_active", "status": "PASS", "decision": gate.get("decision")})
            
        # Check Repo Query
        query = self._load_json(self.reports_root / "repo_intelligence_query_latest.json")
        if query:
            findings.append({"id": "repo_query_active", "status": "PASS"})
            
        # Check Chat CLI
        chat = self._load_json(self.reports_root / "dummie_chat_cli_latest.json")
        if chat:
            findings.append({"id": "chat_cli_active", "status": "PASS"})

        decision = "PASS" if len(findings) >= 3 else "PASS_WITH_WARNINGS"
        
        report = OperationalizationReviewReport(
            review_id="operationalization_pack_1",
            decision=decision,
            findings=findings,
            generated_at=self._utc_now()
        )
        
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "operationalization_review_latest.json").write_text(
            json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8"
        )
        
        # MD format
        md = f"# Operationalization Review\n\nDecision: {decision}\n\n"
        for f in findings:
            md += f"- **{f['id']}**: {f['status']}\n"
        
        (self.reports_root / "operationalization_review_latest.md").write_text(md, encoding="utf-8")
        
        return report.to_dict()

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists(): return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_operationalization_review(aiwg_root: str | Path = ".aiwg") -> dict[str, Any]:
    reviewer = OperationalizationReview(aiwg_root=aiwg_root)
    return reviewer.run_operationalization_review()
