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

    # Generate contract bindings report (validated against current repo state).
    from .bindings import ContractBindingRegistry
    registry = ContractBindingRegistry()
    all_bindings = registry.get_all_bindings()
    repo_root = reports_dir.parent.parent
    findings_by_path = {f.path: f for f in report.findings}
    bindings_rows = []
    for b in all_bindings:
        ev = {}
        finding = findings_by_path.get(b.path)
        if finding:
            ev = {
                "evidence_refs": finding.evidence_refs,
                "related_specs": finding.related_specs,
                "related_tests": finding.related_tests,
                "related_runtime": finding.related_runtime,
            }
        _, validation = registry.evaluate(b.path, repo_root, evidence=ev)
        row = {"binding": b.model_dump(mode="json")}
        if validation:
            row["validation"] = validation.model_dump(mode="json")
        bindings_rows.append(row)

    bindings_json.write_text(json.dumps({"bindings": bindings_rows}, indent=2), encoding="utf-8")
    bindings_md.write_text(_build_bindings_markdown(bindings_rows), encoding="utf-8")

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


def _build_bindings_markdown(bindings_rows: list[dict]) -> str:
    by_status: Dict[str, int] = {}
    for row in bindings_rows:
        status = row.get("validation", {}).get("resolved_status") or row.get("binding", {}).get("binding_status", "UNKNOWN")
        by_status[status] = by_status.get(status, 0) + 1

    lines = [
        "# Structural Contract Bindings",
        "",
        "## Summary",
        f"- Total Bindings: {len(bindings_rows)}",
    ]
    for status, count in sorted(by_status.items()):
        lines.append(f"- {status}: {count}")
    lines.extend(
        [
        "",
        "## Bindings List",
        "",
        "| Path | Layer | Status (declared->resolved) | Risk (declared->effective) | Spec Hits | Test Hits | Issues |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ])
    for row in sorted(bindings_rows, key=lambda x: x["binding"]["path"]):
        b = row["binding"]
        v = row.get("validation", {})
        status_decl = b.get("binding_status", "UNKNOWN")
        status_res = v.get("resolved_status", status_decl)
        risk_decl = b.get("risk_after", "UNKNOWN")
        risk_eff = v.get("effective_risk", risk_decl)
        spec_hits = len(v.get("direct_spec_hits", [])) + len(v.get("scoped_spec_hits", []))
        test_hits = len(v.get("linked_test_hits", []))
        issues = ", ".join(v.get("issues", [])) if v.get("issues") else "none"
        lines.append(
            f"| `{b['path']}` | {b['layer']} | {status_decl}->{status_res} | {risk_decl}->{risk_eff} | {spec_hits} | {test_hits} | {issues} |"
        )
    return "\n".join(lines) + "\n"
