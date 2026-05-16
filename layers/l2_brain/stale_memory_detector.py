from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from layers.l2_brain.freshness_ledger import FreshnessLedger, build_freshness_ledger, load_freshness_ledger


@dataclass
class StaleMemoryFinding:
    artifact_id: str
    finding_type: str
    severity: str
    message: str
    artifact_path: str = ""
    evidence_refs: list[str] = field(default_factory=list)


@dataclass
class StaleMemoryReport:
    generated_at: str
    findings: list[StaleMemoryFinding]

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "findings": [asdict(item) for item in self.findings],
            "summary": self.summary(),
        }

    def summary(self) -> dict[str, int]:
        out = {
            "total": len(self.findings),
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }
        for finding in self.findings:
            out[finding.severity] = out.get(finding.severity, 0) + 1
        return out



def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")



def detect_stale_memory(
    aiwg_root: str | Path = ".aiwg",
    ledger: FreshnessLedger | None = None,
    ledger_path: str | Path = ".aiwg/reports/freshness_ledger.json",
    output_path: str | Path | None = None,
    write_report: bool = True,
) -> StaleMemoryReport:
    aiwg_root_path = Path(aiwg_root)
    repo_root = aiwg_root_path.parent if aiwg_root_path.name == ".aiwg" else aiwg_root_path

    if ledger is None:
        lp = Path(ledger_path)
        if lp.exists():
            ledger = load_freshness_ledger(lp)
        else:
            ledger = build_freshness_ledger(aiwg_root=aiwg_root_path, write_report=write_report)

    findings: list[StaleMemoryFinding] = []

    for entry in ledger.entries:
        if entry.freshness_status == "missing":
            findings.append(
                StaleMemoryFinding(
                    artifact_id=entry.artifact_id,
                    finding_type="missing_artifact",
                    severity="critical",
                    message="Required artifact is missing",
                    artifact_path=entry.artifact_path,
                    evidence_refs=entry.evidence_refs,
                )
            )
        elif entry.freshness_status == "stale":
            findings.append(
                StaleMemoryFinding(
                    artifact_id=entry.artifact_id,
                    finding_type="stale_freshness",
                    severity="high",
                    message="Artifact freshness is stale",
                    artifact_path=entry.artifact_path,
                    evidence_refs=entry.evidence_refs,
                )
            )
        elif entry.freshness_status == "unknown":
            findings.append(
                StaleMemoryFinding(
                    artifact_id=entry.artifact_id,
                    finding_type="unknown_freshness",
                    severity="medium",
                    message="Artifact freshness is unknown",
                    artifact_path=entry.artifact_path,
                    evidence_refs=entry.evidence_refs,
                )
            )

        if "folder_note_hash_mismatch" in entry.risk_flags:
            findings.append(
                StaleMemoryFinding(
                    artifact_id=entry.artifact_id,
                    finding_type="folder_note_hash_mismatch",
                    severity="high",
                    message="Folder note source hash differs from current tracked-files hash",
                    artifact_path=entry.artifact_path,
                    evidence_refs=entry.evidence_refs,
                )
            )

        if "missing_note_path" in entry.risk_flags:
            findings.append(
                StaleMemoryFinding(
                    artifact_id=entry.artifact_id,
                    finding_type="missing_note_path",
                    severity="high",
                    message="Note path is missing",
                    artifact_path=entry.artifact_path,
                    evidence_refs=entry.evidence_refs,
                )
            )

        if "missing_noteplan_path" in entry.risk_flags:
            findings.append(
                StaleMemoryFinding(
                    artifact_id=entry.artifact_id,
                    finding_type="missing_noteplan_path",
                    severity="high",
                    message="NotePlan path is missing",
                    artifact_path=entry.artifact_path,
                    evidence_refs=entry.evidence_refs,
                )
            )

    if not (aiwg_root_path / "world_model" / "project_world_model.json").exists():
        findings.append(
            StaleMemoryFinding(
                artifact_id="project_world_model",
                finding_type="missing_world_model",
                severity="critical",
                message="World model is missing",
                artifact_path=".aiwg/world_model/project_world_model.json",
                evidence_refs=[".aiwg/world_model/project_world_model.json"],
            )
        )

    if not (aiwg_root_path / "reports" / "spec_coverage_matrix.json").exists():
        findings.append(
            StaleMemoryFinding(
                artifact_id="spec_coverage_matrix",
                finding_type="missing_coverage_matrix",
                severity="critical",
                message="Spec coverage matrix is missing",
                artifact_path=".aiwg/reports/spec_coverage_matrix.json",
                evidence_refs=[".aiwg/reports/spec_coverage_matrix.json"],
            )
        )

    report = StaleMemoryReport(generated_at=_utc_now(), findings=findings)

    if write_report:
        target = Path(output_path) if output_path else (aiwg_root_path / "reports" / "stale_memory_report.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")

    return report
