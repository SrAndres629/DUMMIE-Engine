from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class BenchmarkCase:
    strategy: str
    measurement_type: str
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_billable_tokens: int
    kept_context_count: int
    dropped_context_count: int
    compressed_context_count: int
    stale_context_count: int
    required_context_preserved: bool
    value_per_token: float
    cache_reuse_possible: bool
    expected_cloud_context_reduction_ratio: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BenchmarkResult:
    generated_at: str
    baseline_strategy: str
    cases: list[BenchmarkCase]
    decision: str
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "baseline_strategy": self.baseline_strategy,
            "cases": [case.to_dict() for case in self.cases],
            "decision": self.decision,
            "summary": self.summary,
        }


class ContextEfficiencyBenchmark:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"

    def run_context_efficiency_benchmark(self, write_report: bool = True) -> BenchmarkResult:
        package = self._load_json(self.reports_root / "context_package_latest.json")
        receipt = self._load_json(self.reports_root / "context_receipt_latest.json")
        quant = self._load_json(self.reports_root / "context_quant_result_latest.json")
        frame = self._load_json(self.reports_root / "prompt_frame_latest.json")
        stale = self._load_json(self.reports_root / "stale_memory_report.json")
        manifest = self._load_json(self.aiwg_root / "notes" / "folder_notes_manifest.json")
        cache_summary = self._load_json(self.reports_root / "prompt_cache_summary_latest.json")

        package_items = package.get("items", []) if isinstance(package, dict) else []
        raw_input_tokens = max(1, int(sum(item.get("estimated_tokens", 0) for item in package_items) * 2.5))
        raw_kept = len(package_items)
        raw_required_preserved = True

        stale_findings = stale.get("findings", []) if isinstance(stale, dict) else []
        stale_count = sum(1 for f in stale_findings if str(f.get("severity", "")).lower() in {"high", "critical"})

        case_raw = BenchmarkCase(
            strategy="raw_naive_estimate",
            measurement_type="estimated",
            estimated_input_tokens=raw_input_tokens,
            estimated_output_tokens=max(1, int(raw_input_tokens * 0.35)),
            estimated_billable_tokens=max(1, int(raw_input_tokens * 1.35)),
            kept_context_count=raw_kept,
            dropped_context_count=0,
            compressed_context_count=0,
            stale_context_count=stale_count,
            required_context_preserved=raw_required_preserved,
            value_per_token=round((raw_kept * 0.6) / max(1, raw_input_tokens), 6),
            cache_reuse_possible=False,
            expected_cloud_context_reduction_ratio=0.0,
        )

        folder_count = len(manifest.get("folders", [])) if isinstance(manifest, dict) else 0
        folder_input_tokens = max(1, folder_count * 24 + 120)
        case_notes = BenchmarkCase(
            strategy="folder_notes_only",
            measurement_type="estimated",
            estimated_input_tokens=folder_input_tokens,
            estimated_output_tokens=max(1, int(folder_input_tokens * 0.30)),
            estimated_billable_tokens=max(1, int(folder_input_tokens * 1.30)),
            kept_context_count=folder_count,
            dropped_context_count=max(0, raw_kept - folder_count),
            compressed_context_count=0,
            stale_context_count=stale_count,
            required_context_preserved=folder_count > 0,
            value_per_token=round((folder_count * 0.7) / max(1, folder_input_tokens), 6),
            cache_reuse_possible=bool(cache_summary.get("reusable_frames", 0) > 0),
            expected_cloud_context_reduction_ratio=self._ratio(raw_input_tokens, folder_input_tokens, preserved=(folder_count > 0)),
        )

        quant_input_tokens = int(quant.get("estimated_total_tokens", max(1, int(raw_input_tokens * 0.6))))
        quant_kept = len(quant.get("kept_refs", []))
        quant_dropped = len(quant.get("dropped_refs", []))
        quant_compressed = len(quant.get("compressed_refs", []))

        required_refs = {item.get("ref") for item in package_items if bool(item.get("required", False))}
        kept_refs = set(quant.get("kept_refs", []))
        required_preserved = required_refs.issubset(kept_refs)

        # Guard against false claims: if required context is not preserved, no efficiency gain is allowed.
        quant_reduction = self._ratio(raw_input_tokens, quant_input_tokens, preserved=required_preserved)
        if not required_preserved:
            quant_input_tokens = max(quant_input_tokens, raw_input_tokens)

        case_quant = BenchmarkCase(
            strategy="quantized_context_frame",
            measurement_type="estimated",
            estimated_input_tokens=quant_input_tokens,
            estimated_output_tokens=max(1, int(quant_input_tokens * 0.28)),
            estimated_billable_tokens=max(1, int(quant_input_tokens * 1.28)),
            kept_context_count=quant_kept,
            dropped_context_count=quant_dropped,
            compressed_context_count=quant_compressed,
            stale_context_count=stale_count,
            required_context_preserved=required_preserved,
            value_per_token=round((quant_kept * 1.0) / max(1, quant_input_tokens), 6),
            cache_reuse_possible=bool(cache_summary.get("reusable_frames", 0) > 0),
            expected_cloud_context_reduction_ratio=quant_reduction,
        )

        cases = [case_raw, case_notes, case_quant]

        decision = "WARN"
        if case_quant.required_context_preserved and case_quant.expected_cloud_context_reduction_ratio > 0:
            decision = "IMPROVED"
        elif not case_quant.required_context_preserved:
            decision = "DEGRADED_REQUIRED_CONTEXT"

        result = BenchmarkResult(
            generated_at=self._utc_now(),
            baseline_strategy="raw_naive_estimate",
            cases=cases,
            decision=decision,
            summary={
                "best_strategy": max(cases, key=lambda c: c.value_per_token).strategy,
                "raw_input_tokens": case_raw.estimated_input_tokens,
                "quantized_input_tokens": case_quant.estimated_input_tokens,
                "quantized_reduction_ratio": case_quant.expected_cloud_context_reduction_ratio,
                "receipt_decision": receipt.get("decision", "WARN"),
                "frame_ref": ".aiwg/reports/prompt_frame_latest.json" if frame else "",
            },
        )

        if write_report:
            self.reports_root.mkdir(parents=True, exist_ok=True)
            out = self.reports_root / "context_efficiency_benchmark_latest.json"
            out.write_text(json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8")

        return result

    def _ratio(self, raw_tokens: int, strategy_tokens: int, preserved: bool) -> float:
        if raw_tokens <= 0 or not preserved:
            return 0.0
        ratio = (raw_tokens - strategy_tokens) / raw_tokens
        if ratio < 0:
            return 0.0
        if ratio > 1:
            return 1.0
        return round(ratio, 6)

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")



def run_context_efficiency_benchmark(aiwg_root: str | Path = ".aiwg", write_report: bool = True) -> BenchmarkResult:
    runner = ContextEfficiencyBenchmark(aiwg_root=aiwg_root)
    return runner.run_context_efficiency_benchmark(write_report=write_report)
