from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from layers.l2_brain.context_budget_manager import ContextBudgetManager
from layers.l2_brain.freshness_ledger import build_freshness_ledger

FORBIDDEN_TEXT_PATTERNS = [
    re.compile(r"chain_of_thought", re.I),
    re.compile(r"private reasoning", re.I),
    re.compile(r"private_reasoning", re.I),
    re.compile(r"\.env\s*[=:]", re.I),
    re.compile(r"secret\s*(is|[:=])", re.I),
    re.compile(r"credential\s*(is|[:=])", re.I),
    re.compile(r"password\s*[=:]", re.I),
    re.compile(r"api[_-]?key\s*[=:]", re.I),
    re.compile(r"token\s*[=:]", re.I),
]


@dataclass
class ContextItem:
    ref: str
    kind: str
    title: str
    summary: str
    source_path: str
    token_role: str
    truth_rank: int
    freshness_status: str
    estimated_tokens: int
    priority: str
    required: bool
    evidence_refs: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)


@dataclass
class ContextPackage:
    package_id: str
    mission_id: str
    phase: str
    items: list[ContextItem]
    estimated_total_tokens: int
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_id": self.package_id,
            "mission_id": self.mission_id,
            "phase": self.phase,
            "items": [asdict(item) for item in self.items],
            "estimated_total_tokens": self.estimated_total_tokens,
            "created_at": self.created_at,
        }


@dataclass
class ContextReceipt:
    receipt_id: str
    package_id: str
    kept_refs: list[str]
    dropped_refs: list[str]
    compressed_refs: list[str]
    warnings: list[str]
    budget_limit: int
    estimated_total_tokens: int
    decision: str  # ALLOW|WARN|BLOCK

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)



def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")



def _ensure_public_text(value: str) -> str:
    text = str(value)
    for pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(text):
            raise ValueError(f"forbidden private/secret text detected: {text}")
    return text



def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)



def _load_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return default or {}
    return json.loads(path.read_text(encoding="utf-8"))


class ContextPackageBuilder:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"

    def build_context_package(
        self,
        mission_id: str,
        phase: str,
        budget_limit: int | None = None,
        write_outputs: bool = True,
    ) -> tuple[ContextPackage, ContextReceipt]:
        world_model = _load_json(self.aiwg_root / "world_model" / "project_world_model.json")
        current_position = _load_json(self.aiwg_root / "evolution" / "current_position.json")
        next_seed = _load_json(self.aiwg_root / "evolution" / "next_phase_seed.json")
        manifest = _load_json(self.aiwg_root / "notes" / "folder_notes_manifest.json")
        coverage = _load_json(self.aiwg_root / "reports" / "spec_coverage_matrix.json")

        ledger = build_freshness_ledger(aiwg_root=self.aiwg_root, write_report=write_outputs)
        freshness_map = {entry.artifact_id: entry for entry in ledger.entries}

        items: list[ContextItem] = []

        def add_item(item: ContextItem) -> None:
            item.title = _ensure_public_text(item.title)
            item.summary = _ensure_public_text(item.summary)
            item.evidence_refs = [_ensure_public_text(ref) for ref in item.evidence_refs]
            item.risk_flags = [_ensure_public_text(flag) for flag in item.risk_flags]
            items.append(item)

        phase_summary = (
            f"Current phase is {current_position.get('current_phase', 'unknown')} and "
            f"next required phase is {current_position.get('next_required_phase', 'unknown')}."
        )
        add_item(
            ContextItem(
                ref="state:current_position",
                kind="phase_state",
                title="Current Position",
                summary=phase_summary,
                source_path=".aiwg/evolution/current_position.json",
                token_role="summary_only",
                truth_rank=90,
                freshness_status="fresh" if current_position else "missing",
                estimated_tokens=_estimate_tokens(phase_summary),
                priority="critical",
                required=True,
                evidence_refs=[".aiwg/evolution/current_position.json"],
                risk_flags=[] if current_position else ["missing_state_file"],
            )
        )

        seed_summary = (
            f"Next phase seed: {next_seed.get('next_phase', 'unknown')} - {next_seed.get('name', 'unknown')}."
        )
        add_item(
            ContextItem(
                ref="state:next_phase_seed",
                kind="phase_seed",
                title="Next Phase Seed",
                summary=seed_summary,
                source_path=".aiwg/evolution/next_phase_seed.json",
                token_role="summary_only",
                truth_rank=90,
                freshness_status="fresh" if next_seed else "missing",
                estimated_tokens=_estimate_tokens(seed_summary),
                priority="high",
                required=True,
                evidence_refs=[".aiwg/evolution/next_phase_seed.json"],
                risk_flags=[] if next_seed else ["missing_next_seed"],
            )
        )

        wm_summary = (
            f"World model version {world_model.get('version', 'unknown')} with "
            f"next phase {world_model.get('next_phase_requirements', {}).get('next_phase', 'unknown')}."
        )
        wm_status = freshness_map.get("project_world_model").freshness_status if freshness_map.get("project_world_model") else "unknown"
        add_item(
            ContextItem(
                ref="wm:project_world_model",
                kind="world_model",
                title="Project World Model",
                summary=wm_summary,
                source_path=".aiwg/world_model/project_world_model.json",
                token_role="summary_only",
                truth_rank=85,
                freshness_status=wm_status,
                estimated_tokens=_estimate_tokens(wm_summary),
                priority="critical",
                required=True,
                evidence_refs=[".aiwg/world_model/project_world_model.json"],
                risk_flags=[] if wm_status == "fresh" else [f"freshness_{wm_status}"],
            )
        )

        coverage_summary = (
            f"Spec coverage: total {coverage.get('coverage_summary', {}).get('spec_families_total', 0)}, "
            f"complete triplets {coverage.get('coverage_summary', {}).get('complete_triplets', 0)}."
        )
        cov_status = freshness_map.get("spec_coverage_matrix").freshness_status if freshness_map.get("spec_coverage_matrix") else "unknown"
        add_item(
            ContextItem(
                ref="coverage:spec_coverage_matrix",
                kind="coverage",
                title="Spec Coverage Matrix",
                summary=coverage_summary,
                source_path=".aiwg/reports/spec_coverage_matrix.json",
                token_role="summary_only",
                truth_rank=80,
                freshness_status=cov_status,
                estimated_tokens=_estimate_tokens(coverage_summary),
                priority="high",
                required=True,
                evidence_refs=[".aiwg/reports/spec_coverage_matrix.json"],
                risk_flags=[] if cov_status == "fresh" else [f"freshness_{cov_status}"],
            )
        )

        folders = manifest.get("folders", []) if isinstance(manifest.get("folders", []), list) else []
        for folder in folders[:12]:
            folder_id = str(folder.get("folder_id", "unknown"))
            note_path = str(folder.get("note_path", ""))
            note_status = str(folder.get("status", "low_confidence"))
            ledger_key = f"folder_note:{folder_id}"
            freshness = freshness_map.get(ledger_key).freshness_status if freshness_map.get(ledger_key) else "unknown"
            linked_specs = folder.get("linked_specs", [])
            linked_tests = folder.get("linked_tests", [])
            summary = (
                f"Folder {folder_id} status={note_status}, specs={len(linked_specs)}, tests={len(linked_tests)}."
            )
            add_item(
                ContextItem(
                    ref=f"note:{folder_id}",
                    kind="folder_note",
                    title=f"Folder Note {folder_id}",
                    summary=summary,
                    source_path=note_path,
                    token_role=str(folder.get("token_role", "summary_only")),
                    truth_rank=int(folder.get("truth_rank", 40)),
                    freshness_status=freshness,
                    estimated_tokens=_estimate_tokens(summary),
                    priority="medium" if freshness == "fresh" else "low",
                    required=False,
                    evidence_refs=[".aiwg/notes/folder_notes_manifest.json", note_path],
                    risk_flags=list(folder.get("risks", [])),
                )
            )

        total_tokens = sum(item.estimated_tokens for item in items)
        package = ContextPackage(
            package_id=f"pkg-{uuid.uuid4().hex[:12]}",
            mission_id=mission_id,
            phase=phase,
            items=items,
            estimated_total_tokens=total_tokens,
            created_at=_utc_now(),
        )

        budget_manager = ContextBudgetManager()
        budget = budget_manager.allocate_budget("local_fast")
        effective_limit = int(budget_limit if budget_limit is not None else budget.get("total_budget", 4096))

        warnings: list[str] = []
        decision = "ALLOW"
        if total_tokens > effective_limit:
            warnings.append("estimated_tokens_over_budget")
            decision = "WARN"

        receipt = ContextReceipt(
            receipt_id=f"receipt-{uuid.uuid4().hex[:12]}",
            package_id=package.package_id,
            kept_refs=[item.ref for item in items],
            dropped_refs=[],
            compressed_refs=[],
            warnings=warnings,
            budget_limit=effective_limit,
            estimated_total_tokens=total_tokens,
            decision=decision,
        )

        if write_outputs:
            self.reports_root.mkdir(parents=True, exist_ok=True)
            (self.reports_root / "context_package_latest.json").write_text(
                json.dumps(package.to_dict(), indent=2) + "\n", encoding="utf-8"
            )
            (self.reports_root / "context_receipt_latest.json").write_text(
                json.dumps(receipt.to_dict(), indent=2) + "\n", encoding="utf-8"
            )

        return package, receipt
