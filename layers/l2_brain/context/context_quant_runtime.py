from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from layers.l2_brain.context_budget_manager import ContextBudgetManager
from layers.l2_brain.context_package import (
    ContextItem,
    ContextPackage,
    ContextPackageBuilder,
    ContextReceipt,
)
from layers.l2_brain.context.context_role_filter import filter_context_items_by_role
from layers.l2_brain.context_value_scorer import ContextValueScorer
from layers.l2_brain.stale_memory_detector import detect_stale_memory


@dataclass
class ContextQuantResult:
    result_id: str
    package_id: str
    mission_id: str
    phase: str
    kept_refs: list[str]
    dropped_refs: list[str]
    compressed_refs: list[str]
    selected_items: list[dict[str, Any]]
    estimated_total_tokens: int
    budget_limit: int
    decision: str
    warnings: list[str] = field(default_factory=list)
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


class ContextQuantRuntime:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"
        self.builder = ContextPackageBuilder(aiwg_root=self.aiwg_root)
        self.scorer = ContextValueScorer()
        self.budget_manager = ContextBudgetManager()

    def build_context_for_phase(
        self,
        mission_id: str,
        phase: str,
        session_role: str | None = None,
        budget_limit: int | None = None,
        model_tier: str = "local_fast",
        write_outputs: bool = True,
    ) -> ContextQuantResult:
        package, _ = self.builder.build_context_package(
            mission_id=mission_id,
            phase=phase,
            budget_limit=budget_limit,
            write_outputs=write_outputs,
        )

        stale_report = detect_stale_memory(
            aiwg_root=self.aiwg_root, write_report=write_outputs
        )

        budget = self.budget_manager.allocate_budget(model_tier)
        limit = int(
            budget_limit
            if budget_limit is not None
            else budget.get("total_budget", 4096)
        )

        role_items = filter_context_items_by_role(
            package.items, session_role=session_role
        )

        scores = self.scorer.rank_context_items(role_items, phase=phase)
        score_map = {score.ref: score for score in scores}

        required_items = [item for item in role_items if item.required]
        optional_items = [item for item in role_items if not item.required]
        optional_items.sort(
            key=lambda it: (
                score_map.get(it.ref).value_per_token
                if score_map.get(it.ref)
                else -999.0,
                score_map.get(it.ref).value_score if score_map.get(it.ref) else -999.0,
            ),
            reverse=True,
        )

        kept: list[ContextItem] = []
        compressed_refs: list[str] = []
        dropped_refs: list[str] = []

        token_total = 0
        for item in required_items:
            kept.append(item)
            token_total += item.estimated_tokens

        for item in optional_items:
            score = score_map.get(item.ref)
            if score is None:
                dropped_refs.append(item.ref)
                continue

            stale_or_risky = (
                item.freshness_status in {"stale", "missing"}
                or "missing_note_path" in item.risk_flags
                or "missing_noteplan_path" in item.risk_flags
            )
            if stale_or_risky and score.decision != "required":
                if item.token_role == "summary_only":
                    compressed_refs.append(item.ref)
                else:
                    dropped_refs.append(item.ref)
                continue

            if score.decision == "drop":
                dropped_refs.append(item.ref)
                continue

            if token_total + item.estimated_tokens <= limit:
                kept.append(item)
                token_total += item.estimated_tokens
            else:
                compressed_refs.append(item.ref)

        warnings: list[str] = []
        if stale_report.findings:
            warnings.append("stale_memory_findings_present")
        if token_total > limit:
            warnings.append("required_items_exceed_budget")

        decision = "ALLOW"
        if token_total > limit:
            decision = "BLOCK"
        elif warnings or compressed_refs:
            decision = "WARN"

        receipt = ContextReceipt(
            receipt_id=f"receipt-{uuid.uuid4().hex[:12]}",
            package_id=package.package_id,
            kept_refs=[item.ref for item in kept],
            dropped_refs=dropped_refs,
            compressed_refs=compressed_refs,
            warnings=warnings,
            budget_limit=limit,
            estimated_total_tokens=token_total,
            decision=decision,
        )

        result = ContextQuantResult(
            result_id=f"cqr-{uuid.uuid4().hex[:12]}",
            package_id=package.package_id,
            mission_id=mission_id,
            phase=phase,
            kept_refs=receipt.kept_refs,
            dropped_refs=receipt.dropped_refs,
            compressed_refs=receipt.compressed_refs,
            selected_items=[asdict(item) for item in kept],
            estimated_total_tokens=token_total,
            budget_limit=limit,
            decision=decision,
            warnings=warnings,
            created_at=_utc_now(),
        )

        if write_outputs:
            self.reports_root.mkdir(parents=True, exist_ok=True)
            (self.reports_root / "context_receipt_latest.json").write_text(
                json.dumps(receipt.to_dict(), indent=2) + "\n", encoding="utf-8"
            )
            (self.reports_root / "context_quant_result_latest.json").write_text(
                json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8"
            )

        return result
