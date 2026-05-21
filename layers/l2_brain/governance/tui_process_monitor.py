# Spec: DE-V2-L2-118
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ProcessMonitorSnapshot:
    current_phase: str
    next_phase: str
    restart_gate_decision: str
    flywheel_decision: str
    context_efficiency_decision: str
    cache_hit_ratio: float
    stale_findings: int
    known_warnings: list[str] = field(default_factory=list)
    recommended_action: str = ""
    decision: str = "PASS"
    warnings: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TuiProcessMonitor:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"

    def build_process_monitor_snapshot(
        self, write_output: bool = True
    ) -> ProcessMonitorSnapshot:
        warnings: list[str] = []
        evidence_refs: list[str] = []

        current = self._load_json(
            self.aiwg_root / "evolution" / "current_position.json",
            warnings,
            evidence_refs,
        )
        seed = self._load_json(
            self.aiwg_root / "evolution" / "next_phase_seed.json",
            warnings,
            evidence_refs,
        )
        restart = self._load_json(
            self.reports_root / "restart_integration_gate_latest.json",
            warnings,
            evidence_refs,
        )
        bench = self._load_json(
            self.reports_root / "context_efficiency_benchmark_latest.json",
            warnings,
            evidence_refs,
        )
        fly = self._load_json(
            self.reports_root / "evolution_flywheel_latest.json",
            warnings,
            evidence_refs,
        )
        cache = self._load_json(
            self.reports_root / "prompt_cache_summary_latest.json",
            warnings,
            evidence_refs,
        )
        stale = self._load_json(
            self.reports_root / "stale_memory_report.json", warnings, evidence_refs
        )
        quant = self._load_json(
            self.reports_root / "context_quant_result_latest.json",
            warnings,
            evidence_refs,
        )

        stale_findings = (
            len(stale.get("findings", [])) if isinstance(stale, dict) else 0
        )
        cache_hit = float(cache.get("cache_hit_ratio", 0.0) or 0.0)

        recommended = str(fly.get("decision", "review_runtime_outputs"))
        if recommended == "continue_next_phase":
            recommended = f"advance_to_{seed.get('next_phase', 'unknown')}"

        decision = "PASS"
        if str(restart.get("decision", "FAIL")) == "FAIL":
            decision = "FAIL"
        elif warnings or stale_findings > 0:
            decision = "PASS_WITH_WARNINGS"

        snapshot = ProcessMonitorSnapshot(
            current_phase=str(current.get("current_phase", "unknown")),
            next_phase=str(seed.get("next_phase", "unknown")),
            restart_gate_decision=str(restart.get("decision", "UNKNOWN")),
            flywheel_decision=str(fly.get("decision", "UNKNOWN")),
            context_efficiency_decision=str(bench.get("decision", "UNKNOWN")),
            cache_hit_ratio=cache_hit,
            stale_findings=stale_findings,
            known_warnings=list(fly.get("blocking_reasons", [])),
            recommended_action=recommended,
            decision=decision,
            warnings=warnings,
            evidence_refs=evidence_refs
            + [".aiwg/reports/context_quant_result_latest.json"],
            generated_at=self._utc_now(),
        )

        if write_output:
            self.reports_root.mkdir(parents=True, exist_ok=True)
            (self.reports_root / "process_monitor_latest.json").write_text(
                json.dumps(snapshot.to_dict(), indent=2) + "\n", encoding="utf-8"
            )
            (self.reports_root / "process_monitor_latest.txt").write_text(
                self.render_monitor_text(snapshot), encoding="utf-8"
            )

        return snapshot

    def render_monitor_text(self, snapshot: ProcessMonitorSnapshot) -> str:
        return "\n".join(
            [
                "DUMMIE Process Monitor",
                "=====================",
                f"Current phase: {snapshot.current_phase}",
                f"Next phase: {snapshot.next_phase}",
                f"Restart gate: {snapshot.restart_gate_decision}",
                f"Flywheel decision: {snapshot.flywheel_decision}",
                f"Context efficiency: {snapshot.context_efficiency_decision}",
                f"Cache hit ratio: {snapshot.cache_hit_ratio:.3f}",
                f"Stale findings: {snapshot.stale_findings}",
                f"Decision: {snapshot.decision}",
                f"Recommended action: {snapshot.recommended_action}",
                f"Warnings: {', '.join(snapshot.warnings) if snapshot.warnings else 'none'}",
            ]
        )

    def _load_json(
        self, path: Path, warnings: list[str], refs: list[str]
    ) -> dict[str, Any]:
        refs.append(path.as_posix().replace("/media/datasets/DUMMIE Engine/", ""))
        if not path.exists():
            warnings.append(f"missing:{path.name}")
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            warnings.append(f"invalid_json:{path.name}")
            return {}

    def _utc_now(self) -> str:
        return (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )


def build_process_monitor_snapshot(
    aiwg_root: str | Path = ".aiwg", write_output: bool = True
) -> ProcessMonitorSnapshot:
    return TuiProcessMonitor(aiwg_root=aiwg_root).build_process_monitor_snapshot(
        write_output=write_output
    )


def render_monitor_text(snapshot: ProcessMonitorSnapshot) -> str:
    return TuiProcessMonitor().render_monitor_text(snapshot)
