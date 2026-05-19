from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .contracts import Recommendation, RiskLevel, StructuralClass, StructuralTriageReport


def write_reports(
    report: StructuralTriageReport,
    reports_dir: Path,
    max_actions: int = 50,
) -> Dict[str, Path]:
    reports_dir.mkdir(parents=True, exist_ok=True)

    triage_json = reports_dir / "structural_hardening_triage_latest.json"
    triage_md = reports_dir / "structural_hardening_triage_latest.md"
    actions_json = reports_dir / "structural_hardening_actions_latest.json"
    actions_md = reports_dir / "structural_hardening_actions_latest.md"
    bindings_json = reports_dir / "structural_contract_bindings_latest.json"
    bindings_md = reports_dir / "structural_contract_bindings_latest.md"

    triage_json.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    triage_md.write_text(_build_triage_markdown(report, max_actions=max_actions), encoding="utf-8")

    action_rows = [f.model_dump(mode="json") for f in report.top_actions[:max_actions]]
    actions_json.write_text(json.dumps({"actions": action_rows}, indent=2), encoding="utf-8")
    actions_md.write_text(_build_actions_markdown(report, max_actions=max_actions), encoding="utf-8")

    # Generate contract bindings report
    from .bindings import ContractBindingRegistry
    registry = ContractBindingRegistry()
    all_bindings = registry.get_all_bindings()
    bindings_rows = [b.model_dump(mode="json") for b in all_bindings]
    bindings_json.write_text(json.dumps({"bindings": bindings_rows}, indent=2), encoding="utf-8")
    bindings_md.write_text(_build_bindings_markdown(all_bindings), encoding="utf-8")

    return {
        "triage_json": triage_json,
        "triage_md": triage_md,
        "actions_json": actions_json,
        "actions_md": actions_md,
        "bindings_json": bindings_json,
        "bindings_md": bindings_md,
    }



def _build_triage_markdown(report: StructuralTriageReport, max_actions: int) -> str:
    by_class = report.summary_counts.get("by_class", {})
    by_risk = report.summary_counts.get("by_risk", {})
    by_rec = report.summary_counts.get("by_recommendation", {})

    orphan_count = by_class.get(StructuralClass.ORPHAN_TEST_CANDIDATE.value, 0)
    shadow_count = by_class.get(StructuralClass.SHADOW_CANDIDATE.value, 0)

    false_positive_init = sum(
        1
        for f in report.findings
        if f.path.endswith("__init__.py") and f.proposed_class == StructuralClass.ACTIVE_RUNTIME and f.risk == RiskLevel.LOW
    )

    frozen_candidates = [f for f in report.findings if f.recommendation in {Recommendation.FREEZE_UNTIL_REVIEW, Recommendation.MARK_EXPERIMENTAL}]

    lines: List[str] = []
    lines.append("# Structural Hardening Pack 2 - Contract-First Triage")
    lines.append("")
    lines.append("## Status")
    lines.append(f"- pack_status: {report.pack_status}")
    lines.append(f"- repo_health_status: {report.repo_health_status}")
    lines.append(f"- base_commit: {report.base_commit}")
    lines.append(f"- files_analyzed: {report.files_analyzed}")
    lines.append("")

    lines.append("## Counts by Class")
    for k, v in sorted(by_class.items()):
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("## Counts by Recommendation")
    for k, v in sorted(by_rec.items()):
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("## Counts by Risk")
    for k, v in sorted(by_risk.items()):
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("## Top 30 High-Risk Actions")
    top = [f for f in report.top_actions if f.risk in {RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM}][:30]
    if not top:
        lines.append("- none")
    else:
        for i, action in enumerate(top, 1):
            lines.append(
                f"{i}. {action.path} | proposed={action.proposed_class.value} | risk={action.risk.value} | rec={action.recommendation.value} | confidence={action.confidence:.2f}"
            )
    lines.append("")

    lines.append("## False-Positive Corrections")
    lines.append(f"- init_runtime_low_risk_corrections: {false_positive_init}")
    lines.append("")

    lines.append("## Frozen / No-Touch Candidates")
    lines.append(f"- frozen_count: {len(frozen_candidates)}")
    for row in frozen_candidates[:20]:
        lines.append(f"- {row.path} | {row.recommendation.value} | risk={row.risk.value}")
    lines.append("")

    lines.append("## Generated / Legacy Summary")
    lines.append(f"- generated: {by_class.get(StructuralClass.GENERATED.value, 0)}")
    lines.append(f"- legacy: {by_class.get(StructuralClass.LEGACY.value, 0)}")
    lines.append("")

    lines.append("## Orphan Test Candidates")
    lines.append(f"- orphan_test_candidates: {orphan_count}")
    lines.append(f"- shadow_candidates: {shadow_count}")
    lines.append("")

    lines.append("## Next Phase")
    lines.append(report.next_recommended_phase)
    lines.append("")

    lines.append("## Limitations")
    for lim in report.limitations:
        lines.append(f"- {lim}")

    return "\n".join(lines) + "\n"


def _build_actions_markdown(report: StructuralTriageReport, max_actions: int) -> str:
    lines = ["# Structural Hardening Actions", "", "## Top Actions"]
    for i, action in enumerate(report.top_actions[:max_actions], 1):
        lines.append(
            f"{i}. {action.path} | rec={action.recommendation.value} | risk={action.risk.value} | current={action.current_class.value} | proposed={action.proposed_class.value}"
        )
    if len(lines) == 3:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def _build_bindings_markdown(bindings: list) -> str:
    lines = [
        "# Structural Contract Bindings",
        "",
        "## Summary",
        f"- Total Bindings: {len(bindings)}",
        "",
        "## Bindings List",
        "",
        "| Path | Layer | Owner Domain | Status | Spec Refs | Test Refs | Risk After | Notes |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for b in sorted(bindings, key=lambda x: x.path):
        specs_str = ", ".join(b.spec_refs) if b.spec_refs else "None"
        tests_str = ", ".join(b.test_refs) if b.test_refs else "None"
        lines.append(
            f"| `{b.path}` | {b.layer} | {b.owner_domain} | **{b.binding_status.value}** | {specs_str} | {tests_str} | `{b.risk_after.value}` | {b.notes} |"
        )
    return "\n".join(lines) + "\n"

