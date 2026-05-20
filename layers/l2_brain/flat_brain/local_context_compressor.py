# Spec: DE-V2-L2-120
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_FORBIDDEN = [
    re.compile(r"chain_of_thought", re.I),
    re.compile(r"private reasoning\s*[:=]", re.I),
    re.compile(r"private_reasoning", re.I),
    re.compile(r"\.env\s*[=:]", re.I),
    re.compile(r"secret\s*(is|[:=])", re.I),
    re.compile(r"credential\s*(is|[:=])", re.I),
    re.compile(r"password\s*[=:]", re.I),
    re.compile(r"api[_-]?key\s*[=:]", re.I),
    re.compile(r"token\s*[=:]", re.I),
]


@dataclass
class CompressionInput:
    ref: str
    summary: str
    token_role: str
    truth_rank: int
    freshness_status: str
    required: bool
    estimated_tokens: int
    risk_flags: list[str] = field(default_factory=list)


@dataclass
class CompressedContextItem:
    ref: str
    decision: str  # preserve|compress|drop
    summary: str
    input_estimated_tokens: int
    output_estimated_tokens: int
    required: bool
    reason: str


class LocalContextCompressor:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"

    def compress_context_items(self, items: list[CompressionInput]) -> dict[str, Any]:
        compressed_items: list[CompressedContextItem] = []

        input_tokens = 0
        output_tokens = 0
        preserve_count = 0
        compress_count = 0
        drop_count = 0
        required_preserved = True
        warnings: list[str] = []

        for item in items:
            self._check_safe(item.ref)
            self._check_safe(item.summary)
            input_tokens += max(0, int(item.estimated_tokens))

            decision, reason, out_tokens, out_summary = self._decide(item)

            if item.required and decision == "drop":
                # hard safety: required items never dropped
                decision = "preserve"
                reason = reason + "; required_guard_override"
                out_tokens = max(1, min(max(1, item.estimated_tokens), 96))
                out_summary = self._compress_text(item.summary, max_chars=360)

            if item.required and decision != "drop":
                preserve_count += 1
            elif decision == "preserve":
                preserve_count += 1
            elif decision == "compress":
                compress_count += 1
            else:
                drop_count += 1

            if item.required and decision == "drop":
                required_preserved = False

            output_tokens += out_tokens

            compressed_items.append(
                CompressedContextItem(
                    ref=item.ref,
                    decision=decision,
                    summary=out_summary,
                    input_estimated_tokens=max(0, int(item.estimated_tokens)),
                    output_estimated_tokens=out_tokens,
                    required=item.required,
                    reason=reason,
                )
            )

            if item.freshness_status in {"stale", "unknown", "missing"} and item.required:
                warnings.append(f"required_item_{item.ref}_freshness_{item.freshness_status}")

        reduction_ratio = 0.0
        if input_tokens > 0:
            reduction_ratio = max(0.0, min(1.0, (input_tokens - output_tokens) / input_tokens))

        return {
            "input_estimated_tokens": input_tokens,
            "output_estimated_tokens": output_tokens,
            "reduction_ratio": round(reduction_ratio, 6),
            "items_preserved": preserve_count,
            "items_compressed": compress_count,
            "items_dropped": drop_count,
            "required_preserved": required_preserved,
            "warnings": sorted(set(warnings)),
            "items": [asdict(item) for item in compressed_items],
        }

    def compress_latest_context(self, write_output: bool = True) -> dict[str, Any]:
        package = self._load_json(self.reports_root / "context_package_latest.json")
        frame = self._load_json(self.reports_root / "prompt_frame_latest.json")

        items = []
        for row in package.get("items", []):
            items.append(
                CompressionInput(
                    ref=str(row.get("ref", "")),
                    summary=str(row.get("summary", "")),
                    token_role=str(row.get("token_role", "summary_only")),
                    truth_rank=int(row.get("truth_rank", 0) or 0),
                    freshness_status=str(row.get("freshness_status", "unknown")),
                    required=bool(row.get("required", False)),
                    estimated_tokens=int(row.get("estimated_tokens", 0) or 0),
                    risk_flags=list(row.get("risk_flags", []) or []),
                )
            )

        for section_name, lines in (frame.get("prompt_sections", {}) or {}).items():
            if not isinstance(lines, list):
                continue
            text = " ".join(str(x) for x in lines)
            if not text.strip():
                continue
            items.append(
                CompressionInput(
                    ref=f"frame_section:{section_name}",
                    summary=text,
                    token_role="summary_only",
                    truth_rank=70,
                    freshness_status="fresh",
                    required=section_name in {"system", "mission"},
                    estimated_tokens=max(1, len(text) // 4),
                    risk_flags=[],
                )
            )

        payload = self.compress_context_items(items)
        payload["generated_at"] = self._utc_now()
        payload["source_refs"] = [
            ".aiwg/reports/context_package_latest.json",
            ".aiwg/reports/prompt_frame_latest.json",
        ]

        if write_output:
            self.reports_root.mkdir(parents=True, exist_ok=True)
            out = self.reports_root / "local_context_compression_latest.json"
            out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

        return payload

    def _decide(self, item: CompressionInput) -> tuple[str, str, int, str]:
        role = item.token_role
        fresh = item.freshness_status
        risk = len(item.risk_flags)
        est = max(1, int(item.estimated_tokens))

        if role == "never_prompt":
            return "drop", "token_role_never_prompt", 0, ""

        if item.required:
            summary = self._compress_text(item.summary, max_chars=420)
            return "preserve", "required_item", max(1, min(est, max(32, est // 2))), summary

        if any(x in role for x in ["human_mirror", "debug_only"]):
            return "drop", f"token_role_{role}", 0, ""

        if fresh in {"stale", "missing"}:
            if role == "retrieval_candidate":
                summary = f"ref_only:{item.ref}"
                return "compress", "stale_retrieval_candidate_ref_only", 6, summary
            return "drop", f"freshness_{fresh}", 0, ""

        if fresh == "unknown":
            summary = self._compress_text(item.summary, max_chars=180)
            return "compress", "unknown_freshness", max(1, min(est, 24)), summary

        if risk >= 2:
            summary = self._compress_text(item.summary, max_chars=160)
            return "compress", "risk_flags_present", max(1, min(est, 20)), summary

        if role in {"summary_only", "retrieval_candidate"}:
            summary = self._compress_text(item.summary, max_chars=220)
            out_tokens = max(1, min(est, max(12, est // 3)))
            return "compress", f"token_role_{role}", out_tokens, summary

        summary = self._compress_text(item.summary, max_chars=260)
        out_tokens = max(1, min(est, max(16, est // 2)))
        return "preserve", "default_preserve", out_tokens, summary

    def _compress_text(self, text: str, max_chars: int) -> str:
        t = " ".join(str(text).split())
        if len(t) <= max_chars:
            return t
        return t[: max_chars - 1] + "…"

    def _check_safe(self, value: str) -> None:
        for pattern in _FORBIDDEN:
            if pattern.search(str(value)):
                raise ValueError(f"forbidden secret/private content detected: {value}")

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compress_context_items(items: list[CompressionInput], aiwg_root: str | Path = ".aiwg") -> dict[str, Any]:
    return LocalContextCompressor(aiwg_root=aiwg_root).compress_context_items(items)


def compress_latest_context(aiwg_root: str | Path = ".aiwg", write_output: bool = True) -> dict[str, Any]:
    return LocalContextCompressor(aiwg_root=aiwg_root).compress_latest_context(write_output=write_output)
