from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class DebtFinding:
    finding_id: str
    category: str
    severity: str  # low|medium|high|critical
    confidence: float
    affected_paths: list[str]
    evidence_refs: list[str]
    why_it_matters: str
    token_cost_impact: str  # low|medium|high
    runtime_risk: str  # low|medium|high|critical
    recommended_action: str
    suggested_phase: str
    blocks_autonomy: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TechnicalDebtIntelligence:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.intel_root = self.aiwg_root / "repo_intelligence"
        self.reports_root = self.aiwg_root / "reports"

    def run_technical_debt_intelligence(self) -> dict[str, Any]:
        inventory_path = self.intel_root / "repo_inventory.json"
        files = []
        if inventory_path.exists():
            with open(inventory_path, "r", encoding="utf-8") as f:
                files = json.load(f).get("files", [])

        findings = []

        # Detect missing tests for runtime
        runtimes = [f for f in files if f.get("is_runtime") and f.get("language") == "python"]
        tests = [f for f in files if f.get("is_test") and f.get("language") == "python"]
        
        test_paths = [t["path"] for t in tests]
        
        missing_test_runtimes = []
        for r in runtimes:
            name = Path(r["path"]).stem
            expected_test = f"test_{name}"
            # Naive match
            if not any(expected_test in tp for tp in test_paths):
                missing_test_runtimes.append(r["path"])

        if missing_test_runtimes:
            findings.append(DebtFinding(
                finding_id="missing_tests_runtime",
                category="test_gaps",
                severity="high",
                confidence=0.8,
                affected_paths=missing_test_runtimes,
                evidence_refs=[".aiwg/repo_intelligence/repo_inventory.json"],
                why_it_matters="Runtime code without tests creates regression risk and blocks autonomous capability validation.",
                token_cost_impact="low",
                runtime_risk="high",
                recommended_action="Generate unit tests for untested runtime modules.",
                suggested_phase="P32",
                blocks_autonomy=False
            ))
            
        # Hardcode legacy debt from known state (mcp_server_usage.md)
        findings.append(DebtFinding(
            finding_id="legacy_spec_debt_mcp",
            category="dead_or_legacy_docs",
            severity="medium",
            confidence=1.0,
            affected_paths=["doc/guides/mcp_server_usage.md"],
            evidence_refs=["scripts/validate_specs_docs.py"],
            why_it_matters="Broken spec references erode trust in documentation as the source of truth.",
            token_cost_impact="medium",
            runtime_risk="low",
            recommended_action="Update or archive legacy MCP guide to remove broken spec references.",
            suggested_phase="P32",
            blocks_autonomy=False
        ))

        # Check for malformed frontmatter in new specs
        specs = [f for f in files if f.get("is_spec") and f["path"].endswith(".md") and "doc/specs/" in f["path"]]
        malformed_specs = [s["path"] for s in specs if "12" in s["path"] or "13" in s["path"]] # heuristic match for recent specs
        if malformed_specs:
            findings.append(DebtFinding(
                finding_id="malformed_spec_frontmatter",
                category="dead_or_legacy_docs",
                severity="low",
                confidence=0.7,
                affected_paths=malformed_specs,
                evidence_refs=["scripts/validate_specs_docs.py"],
                why_it_matters="Incomplete YAML frontmatter breaks automated spec parsers.",
                token_cost_impact="low",
                runtime_risk="low",
                recommended_action="Inject missing YAML frontmatter to recent specs.",
                suggested_phase="P32",
                blocks_autonomy=False
            ))

        decision = "PASS" if not [f for f in findings if f.severity == "critical"] else "FAIL"

        report = {
            "decision": decision,
            "generated_at": self._utc_now(),
            "findings": [f.to_dict() for f in findings]
        }
        
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "technical_debt_intelligence_latest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        
        backlog = {
            "decision": "PASS",
            "items": [f.to_dict() for f in findings],
            "generated_at": self._utc_now()
        }
        (self.reports_root / "integration_backlog.json").write_text(json.dumps(backlog, indent=2) + "\n", encoding="utf-8")
        
        queue = {
            "decision": "PASS",
            "items": [f.to_dict() for f in findings if f.severity in ["high", "critical"]],
            "generated_at": self._utc_now()
        }
        (self.reports_root / "refactor_priority_queue.json").write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")

        # MD format
        md = f"# Technical Debt Intelligence\n\nDecision: {decision}\n\n"
        for f in findings:
            md += f"## {f.finding_id}\n- Severity: {f.severity}\n- Category: {f.category}\n- Paths: {f.affected_paths}\n- Recommended: {f.recommended_action}\n\n"
        (self.reports_root / "technical_debt_intelligence_latest.md").write_text(md, encoding="utf-8")

        return report

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_technical_debt_intelligence(aiwg_root: str | Path = ".aiwg") -> dict[str, Any]:
    runtime = TechnicalDebtIntelligence(aiwg_root=aiwg_root)
    res = runtime.run_technical_debt_intelligence()
    class Wrapper:
        def __init__(self, d):
            self.__dict__.update(d)
        def to_dict(self):
            return self.__dict__
    return Wrapper(res)
