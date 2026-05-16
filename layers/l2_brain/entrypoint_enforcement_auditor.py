from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class EntrypointEnforcementAudit:
    entrypoint: str
    bypasses_context_gate: bool
    uses_repo_intelligence: bool
    records_outcome: bool
    records_token_cost: bool
    uses_memory_spine: bool
    writes_latest_report: bool
    is_exposed_by_cli: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EntrypointEnforcementAuditor:
    def __init__(self, repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg"):
        self.repo_root = Path(repo_root).resolve()
        self.aiwg_root = self.repo_root / aiwg_root
        self.reports_root = self.aiwg_root / "reports"

    def run_audit(self) -> dict[str, Any]:
        entrypoints = [
            "dummie_chat_cli",
            "cli_control_plane",
            "autonomous_strategic_partner_runtime",
            "strategic_partner_swarm",
            "debate_review_runtime",
            "mission_planner",
            "context_efficiency_benchmark",
            "dashboard_renderer"
        ]
        
        audits = []
        for ep in entrypoints:
            audits.append(self._audit_entrypoint(ep))
            
        report = {
            "decision": "PASS_WITH_WARNINGS" if any(not a.uses_memory_spine for a in audits) else "PASS",
            "audits": [a.to_dict() for a in audits],
            "generated_at": self._utc_now()
        }

        self._save_report(report)
        return report

    def _audit_entrypoint(self, ep: str) -> EntrypointEnforcementAudit:
        path = self.repo_root / f"layers/l2_brain/{ep}.py"
        if not path.exists():
             # Check layer-specific subfolders if needed, or assume missing
             path = next(self.repo_root.rglob(f"*/{ep}.py"), None)
        
        content = ""
        if path and path.exists():
            content = path.read_text(encoding="utf-8")
            
        return EntrypointEnforcementAudit(
            entrypoint=ep,
            bypasses_context_gate="ContextEnforcementGate" not in content and "enforce_context" not in content,
            uses_repo_intelligence="RepoIntelligence" in content or "repo_intelligence" in content,
            records_outcome="outcome" in content or "DaemonOutcome" in content,
            records_token_cost="TokenCostLedger" in content or "record_usage" in content,
            uses_memory_spine="MemorySpineEntrypoint" in content or "retrieve_memory" in content,
            writes_latest_report="_latest.json" in content or "write_text" in content,
            is_exposed_by_cli=ep in (self.repo_root / "layers/l2_brain/cli_control_plane.py").read_text(encoding="utf-8") if (self.repo_root / "layers/l2_brain/cli_control_plane.py").exists() else False
        )

    def _save_report(self, report: dict[str, Any]):
        self.reports_root.mkdir(parents=True, exist_ok=True)
        (self.reports_root / "entrypoint_enforcement_audit_latest.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        
        md = f"# Entrypoint Enforcement Audit Report\n\n"
        md += f"**Decision:** {report['decision']}\n"
        md += f"**Generated At:** {report['generated_at']}\n\n"
        md += "| Entrypoint | Bypasses Gate | Repo Intel | Outcome | Tokens | Memory Spine | Report | CLI |\n"
        md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for a in report["audits"]:
            md += f"| {a['entrypoint']} | {'❌' if a['bypasses_context_gate'] else '✅'} | {'✅' if a['uses_repo_intelligence'] else '❌'} | {'✅' if a['records_outcome'] else '❌'} | {'✅' if a['records_token_cost'] else '❌'} | {'✅' if a['uses_memory_spine'] else '❌'} | {'✅' if a['writes_latest_report'] else '❌'} | {'✅' if a['is_exposed_by_cli'] else '❌'} |\n"
            
        (self.reports_root / "entrypoint_enforcement_audit_latest.md").write_text(md, encoding="utf-8")

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_entrypoint_enforcement_audit(repo_root: str | Path = ".", aiwg_root: str | Path = ".aiwg") -> dict[str, Any]:
    auditor = EntrypointEnforcementAuditor(repo_root=repo_root, aiwg_root=aiwg_root)
    return auditor.run_audit()


if __name__ == "__main__":
    run_entrypoint_enforcement_audit()
