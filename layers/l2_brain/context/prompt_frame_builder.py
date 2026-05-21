# Spec: DE-V2-L2-113
from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from layers.l2_brain.context_quant_runtime import ContextQuantRuntime

_FORBIDDEN_PATTERNS = [
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

_RAW_DUMP_BLOCKLIST = {
    ".",
    "./",
    "/",
    "layers",
    "doc",
    ".aiwg",
    "layers/",
    "doc/",
    ".aiwg/",
}


@dataclass
class PromptFrame:
    frame_id: str
    mission_id: str
    phase_id: str
    system_refs: list[str]
    mission_refs: list[str]
    context_refs: list[str]
    compressed_refs: list[str]
    dropped_refs: list[str]
    retrieval_refs: list[str]
    token_budget: int
    estimated_tokens: int
    staleness_warnings: list[str]
    truth_policy_refs: list[str]
    prompt_sections: dict[str, list[str]]
    receipt_ref: str
    source_hash: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PromptFrameBuilder:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"

    def build_prompt_frame_for_phase(
        self,
        mission_id: str,
        phase_id: str,
        budget_limit: int = 4096,
        write_output: bool = True,
    ) -> PromptFrame:
        quant_runtime = ContextQuantRuntime(aiwg_root=self.aiwg_root)
        quant_result = quant_runtime.build_context_for_phase(
            mission_id=mission_id,
            phase=phase_id,
            budget_limit=budget_limit,
            write_outputs=write_output,
        )

        package = self._load_json(self.reports_root / "context_package_latest.json")
        receipt = self._load_json(self.reports_root / "context_receipt_latest.json")
        stale_report = self._load_json(self.reports_root / "stale_memory_report.json")

        system_refs = [
            ".aiwg/evolution/current_position.json",
            ".aiwg/evolution/next_phase_seed.json",
            ".aiwg/world_model/project_world_model.json",
            ".aiwg/schemas/truth_hierarchy.schema.json",
            ".aiwg/schemas/cognitive_artifact.schema.json",
        ]
        mission_refs = [
            ".aiwg/reports/context_package_latest.json",
            ".aiwg/reports/context_receipt_latest.json",
            ".aiwg/reports/context_quant_result_latest.json",
        ]
        truth_policy_refs = [
            ".aiwg/schemas/truth_hierarchy.schema.json",
            ".aiwg/schemas/cognitive_artifact.schema.json",
            ".aiwg/evolution/current_position.json",
        ]

        selected_items = list(quant_result.selected_items)
        context_refs = list(quant_result.kept_refs)
        compressed_refs = list(quant_result.compressed_refs)
        dropped_refs = list(quant_result.dropped_refs)

        retrieval_refs = [
            str(item.get("ref", ""))
            for item in selected_items
            if str(item.get("token_role", "")) == "retrieval_candidate"
        ]

        staleness_warnings = self._extract_staleness_warnings(stale_report)

        # Security checks
        for ref in (
            system_refs
            + mission_refs
            + truth_policy_refs
            + context_refs
            + compressed_refs
            + dropped_refs
            + retrieval_refs
        ):
            self._ensure_safe_value(ref)
            self._ensure_not_raw_dump_ref(ref)

        # Build prompt sections (compact and deterministic)
        section_system = [
            "Use canonical state files and truth hierarchy before any derived artifact.",
            "Do not consume raw folder dumps; use references and compressed summaries.",
            "Reject secrets and private reasoning artifacts in context.",
        ]
        section_mission = [
            f"Mission: {mission_id}",
            f"Phase: {phase_id}",
            f"Budget: {quant_result.budget_limit}",
            f"Receipt decision: {receipt.get('decision', 'WARN')}",
        ]
        section_context = []
        for item in selected_items:
            ref = str(item.get("ref", ""))
            summary = str(item.get("summary", ""))
            freshness = str(item.get("freshness_status", "unknown"))
            self._ensure_safe_value(summary)
            section_context.append(f"[{ref}] ({freshness}) {summary}")

        prompt_sections = {
            "system": section_system,
            "mission": section_mission,
            "context": section_context,
            "warnings": staleness_warnings,
        }

        source_hash = self._stable_source_hash(
            phase_id=phase_id,
            mission_id=mission_id,
            context_refs=context_refs,
            compressed_refs=compressed_refs,
            dropped_refs=dropped_refs,
            receipt=receipt,
            selected_items=selected_items,
        )

        frame = PromptFrame(
            frame_id=f"frame-{uuid.uuid4().hex[:12]}",
            mission_id=mission_id,
            phase_id=phase_id,
            system_refs=system_refs,
            mission_refs=mission_refs,
            context_refs=context_refs,
            compressed_refs=compressed_refs,
            dropped_refs=dropped_refs,
            retrieval_refs=retrieval_refs,
            token_budget=int(quant_result.budget_limit),
            estimated_tokens=int(quant_result.estimated_total_tokens),
            staleness_warnings=staleness_warnings,
            truth_policy_refs=truth_policy_refs,
            prompt_sections=prompt_sections,
            receipt_ref=".aiwg/reports/context_receipt_latest.json",
            source_hash=source_hash,
            created_at=self._utc_now(),
        )

        if write_output:
            self.reports_root.mkdir(parents=True, exist_ok=True)
            (self.reports_root / "prompt_frame_latest.json").write_text(
                json.dumps(frame.to_dict(), indent=2) + "\n", encoding="utf-8"
            )

        return frame

    def _extract_staleness_warnings(self, stale_report: dict[str, Any]) -> list[str]:
        findings = (
            stale_report.get("findings", []) if isinstance(stale_report, dict) else []
        )
        warnings = []
        for finding in findings:
            severity = str(finding.get("severity", "")).lower()
            finding_type = str(finding.get("finding_type", ""))
            if severity in {"critical", "high", "medium"} and finding_type:
                self._ensure_safe_value(finding_type)
                warnings.append(finding_type)
        return sorted(set(warnings))

    def _stable_source_hash(
        self,
        *,
        phase_id: str,
        mission_id: str,
        context_refs: list[str],
        compressed_refs: list[str],
        dropped_refs: list[str],
        receipt: dict[str, Any],
        selected_items: list[dict[str, Any]],
    ) -> str:
        payload = {
            "phase_id": phase_id,
            "mission_id": mission_id,
            "context_refs": sorted(context_refs),
            "compressed_refs": sorted(compressed_refs),
            "dropped_refs": sorted(dropped_refs),
            "receipt_decision": receipt.get("decision", "WARN"),
            "receipt_budget": receipt.get("budget_limit", 0),
            "selected": [
                {
                    "ref": item.get("ref", ""),
                    "freshness_status": item.get("freshness_status", "unknown"),
                    "truth_rank": item.get("truth_rank", 0),
                    "token_role": item.get("token_role", "summary_only"),
                }
                for item in selected_items
            ],
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _ensure_safe_value(self, value: str) -> None:
        text = str(value)
        for pattern in _FORBIDDEN_PATTERNS:
            if pattern.search(text):
                raise ValueError(f"unsafe prompt frame content: {text}")

    def _ensure_not_raw_dump_ref(self, ref: str) -> None:
        candidate = str(ref).strip()
        if not candidate:
            return
        normalized = (
            candidate.rstrip("/") + "/" if candidate.endswith("/") else candidate
        )
        if candidate in _RAW_DUMP_BLOCKLIST or normalized in _RAW_DUMP_BLOCKLIST:
            raise ValueError(f"raw repo dump ref is forbidden: {ref}")

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _utc_now(self) -> str:
        return (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )


def build_prompt_frame_for_phase(
    mission_id: str,
    phase_id: str,
    aiwg_root: str | Path = ".aiwg",
    budget_limit: int = 4096,
    write_output: bool = True,
) -> PromptFrame:
    builder = PromptFrameBuilder(aiwg_root=aiwg_root)
    return builder.build_prompt_frame_for_phase(
        mission_id=mission_id,
        phase_id=phase_id,
        budget_limit=budget_limit,
        write_output=write_output,
    )
