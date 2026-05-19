# Spec Reference: 192_embedding_mesh_foundation
import json
from pathlib import Path
from typing import Dict, List, Any
from .contracts import StructuralTriageReport, StructuralClass, RiskLevel, Recommendation


class StructuralHardeningReporter:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.reports_dir = self.repo_root / ".aiwg" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def write_reports(self, report: StructuralTriageReport, max_actions: int = 50) -> Dict[str, str]:
        # Path declarations
        triage_json_path = self.reports_dir / "structural_hardening_triage_latest.json"
        triage_md_path = self.reports_dir / "structural_hardening_triage_latest.md"
        actions_json_path = self.reports_dir / "structural_hardening_actions_latest.json"
        actions_md_path = self.reports_dir / "structural_hardening_actions_latest.md"

        # 1. Write Triage JSON
        triage_json_path.write_text(
            json.dumps(report.model_dump(), indent=2), encoding="utf-8"
        )

        # 2. Write Triage Markdown
        md_content = self._generate_triage_markdown(report)
        triage_md_path.write_text(md_content, encoding="utf-8")

        # 3. Write Actions JSON
        limited_actions = report.top_actions[:max_actions]
        actions_json_path.write_text(
            json.dumps({
                "generated_at": report.generated_at,
                "base_commit": report.base_commit,
                "total_high_risk_actions": len(report.top_actions),
                "actions_returned": len(limited_actions),
                "actions": limited_actions
            }, indent=2), encoding="utf-8"
        )

        # 4. Write Actions Markdown
        actions_md = self._generate_actions_markdown(report, limited_actions)
        actions_md_path.write_text(actions_md, encoding="utf-8")

        return {
            "triage_json": str(triage_json_path),
            "triage_md": str(triage_md_path),
            "actions_json": str(actions_json_path),
            "actions_md": str(actions_md_path)
        }

    def _generate_triage_markdown(self, report: StructuralTriageReport) -> str:
        # Build recommendation and risk counts manually
        rec_counts = {rec.value: 0 for rec in Recommendation}
        risk_counts = {rsk.value: 0 for rsk in RiskLevel}
        
        for f in report.findings:
            rec_counts[f.recommendation.value] = rec_counts.get(f.recommendation.value, 0) + 1
            risk_counts[f.risk.value] = risk_counts.get(f.risk.value, 0) + 1

        lines = [
            "# DUMMIE Engine - Structural Hardening Triage Report",
            "",
            "## Status Calibration",
            f"- pack_name: {report.pack_name}",
            f"- pack_status: {report.pack_status}",
            f"- repo_health_status: {report.repo_health_status}",
            f"- base_commit: {report.base_commit}",
            f"- generated_at: {report.generated_at}",
            f"- files_analyzed: {report.files_analyzed}",
            "",
            "## Summary Counts by Structural Class",
        ]
        for cls_name, count in sorted(report.summary_counts.items()):
            lines.append(f"- {cls_name}: {count}")

        lines.extend([
            "",
            "## Summary Counts by Recommendation",
        ])
        for rec_name, count in sorted(rec_counts.items()):
            lines.append(f"- {rec_name}: {count}")

        lines.extend([
            "",
            "## Summary Counts by Risk Level",
        ])
        for risk_name, count in sorted(risk_counts.items()):
            lines.append(f"- {risk_name}: {count}")

        # Document Packaging Glue Correction
        glue_count = sum(1 for f in report.findings if f.path.endswith("__init__.py") and f.proposed_class == StructuralClass.ACTIVE_RUNTIME)
        lines.extend([
            "",
            "## False-Positive Corrections",
            f"- empty_init_packaging_glue_active: {glue_count} (Classified as ACTIVE_RUNTIME with LOW risk to avoid shadow candidate bloat.)"
        ])

        # Document Top Action Items
        lines.extend([
            "",
            "## Top Unresolved High-Risk Actions",
            "Refer to structural_hardening_actions_latest.md for full descriptive details.",
            f"- total_high_risk_actions: {len(report.top_actions)}"
        ])

        # Limitations
        lines.extend([
            "",
            "## Limitations & Heuristics",
        ])
        for lim in report.limitations:
            lines.append(f"- {lim}")

        lines.extend([
            "",
            "## Next Recommended Phase",
            f"- next_phase: {report.next_recommended_phase}"
        ])

        return "\n".join(lines)

    def _generate_actions_markdown(self, report: StructuralTriageReport, actions: List[Dict[str, Any]]) -> str:
        lines = [
            "# DUMMIE Engine - Top High-Risk Structural Hardening Actions",
            "",
            f"Showing the top {len(actions)} high-risk findings out of {len(report.top_actions)} total actions requiring triage.",
            "",
            "| Priority | File Path | Proposed Class | Risk | Recommended Action | Primary Reasons |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |"
        ]

        for idx, act in enumerate(actions, 1):
            path = act["path"]
            cls = act["proposed_class"]
            risk = act["risk"]
            rec = act["recommendation"]
            reasons = "; ".join(act["reasons"])
            lines.append(f"| {idx} | `{path}` | {cls} | **{risk}** | `{rec}` | {reasons} |")

        return "\n".join(lines)
