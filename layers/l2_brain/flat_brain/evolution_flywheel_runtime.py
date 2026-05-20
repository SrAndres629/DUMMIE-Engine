# Spec: DE-V2-L2-116
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class EvolutionFlywheelSignal:
    name: str
    status: str
    value: Any
    evidence_ref: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvolutionFlywheelDecision:
    decision: str
    snowball_gain_score: float
    confidence: float
    blocking_reasons: list[str]
    recommended_next_phase: str
    why_this_is_the_next_lever: str
    expected_capability_gain: str
    expected_token_efficiency_gain: str
    required_tests_next: list[str]
    signals: list[EvolutionFlywheelSignal] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "snowball_gain_score": self.snowball_gain_score,
            "confidence": self.confidence,
            "blocking_reasons": self.blocking_reasons,
            "recommended_next_phase": self.recommended_next_phase,
            "why_this_is_the_next_lever": self.why_this_is_the_next_lever,
            "expected_capability_gain": self.expected_capability_gain,
            "expected_token_efficiency_gain": self.expected_token_efficiency_gain,
            "required_tests_next": self.required_tests_next,
            "signals": [signal.to_dict() for signal in self.signals],
            "generated_at": self.generated_at,
        }


class EvolutionFlywheelRuntime:
    def __init__(self, aiwg_root: str | Path = ".aiwg"):
        self.aiwg_root = Path(aiwg_root)
        self.reports_root = self.aiwg_root / "reports"

    def run_evolution_flywheel(self, write_report: bool = True) -> EvolutionFlywheelDecision:
        restart = self._load_json(self.reports_root / "restart_integration_gate_latest.json")
        benchmark = self._load_json(self.reports_root / "context_efficiency_benchmark_latest.json")
        cache_summary = self._load_json(self.reports_root / "prompt_cache_summary_latest.json")
        stale = self._load_json(self.reports_root / "stale_memory_report.json")
        current_position = self._load_json(self.aiwg_root / "evolution" / "current_position.json")
        next_seed = self._load_json(self.aiwg_root / "evolution" / "next_phase_seed.json")

        restart_decision = str(restart.get("decision", "FAIL"))
        benchmark_decision = str(benchmark.get("decision", "WARN"))
        stale_findings = stale.get("findings", []) if isinstance(stale, dict) else []
        high_stale = sum(1 for item in stale_findings if str(item.get("severity", "")).lower() in {"high", "critical"})
        reduction = float(benchmark.get("summary", {}).get("quantized_reduction_ratio", 0.0) or 0.0)
        cache_hit = float(cache_summary.get("cache_hit_ratio", 0.0) or 0.0)

        blocking: list[str] = []
        decision = "continue_next_phase"
        confidence = 0.55

        if restart_decision == "FAIL":
            decision = "repair_before_next_phase"
            blocking.append("restart_integration_gate_failed")
            confidence = 0.95
        elif benchmark_decision == "DEGRADED_REQUIRED_CONTEXT":
            decision = "repair_before_next_phase"
            blocking.append("benchmark_lost_required_context")
            confidence = 0.9
        elif benchmark_decision not in {"IMPROVED", "WARN"}:
            decision = "rerun_benchmark"
            blocking.append("benchmark_not_actionable")
            confidence = 0.75
        elif high_stale > 0 and reduction < 0.1:
            decision = "refresh_notes"
            blocking.append("stale_memory_pressure")
            confidence = 0.7

        if restart_decision == "FAIL" and high_stale > 0:
            decision = "block_due_to_runtime_failure"
            confidence = 0.98

        gain = max(0.0, reduction * 10.0 + cache_hit * 5.0 - high_stale * 1.5)
        next_phase = str(next_seed.get("next_phase", "P18"))
        if decision in {"repair_before_next_phase", "rerun_benchmark", "refresh_notes", "block_due_to_runtime_failure"}:
            recommended_next_phase = str(current_position.get("current_phase", "P17"))
        else:
            recommended_next_phase = next_phase

        why = (
            "P18 can be attempted because runtime gates and context efficiency are within controlled bounds."
            if decision == "continue_next_phase"
            else "Runtime evidence indicates remediation is required before advancing phase scope."
        )

        expected_capability_gain = (
            "Reusable prompt framing + cache-aware control plane bootstrap readiness."
            if decision == "continue_next_phase"
            else "Stabilized runtime reliability before control-plane expansion."
        )
        expected_token_gain = (
            f"Estimated context input reduction ratio {reduction:.3f} with cache hit ratio {cache_hit:.3f}."
            if decision == "continue_next_phase"
            else "Token efficiency gains deferred until blocking issues are corrected."
        )

        signals = [
            EvolutionFlywheelSignal(
                name="restart_gate",
                status=restart_decision,
                value=restart_decision,
                evidence_ref=".aiwg/reports/restart_integration_gate_latest.json",
            ),
            EvolutionFlywheelSignal(
                name="benchmark",
                status=benchmark_decision,
                value=benchmark.get("summary", {}),
                evidence_ref=".aiwg/reports/context_efficiency_benchmark_latest.json",
            ),
            EvolutionFlywheelSignal(
                name="cache_summary",
                status="PASS" if cache_summary else "WARN",
                value={
                    "cache_hit_ratio": cache_hit,
                    "reusable_frames": cache_summary.get("reusable_frames", 0),
                },
                evidence_ref=".aiwg/reports/prompt_cache_summary_latest.json",
            ),
            EvolutionFlywheelSignal(
                name="stale_memory",
                status="WARN" if high_stale > 0 else "PASS",
                value={"high_or_critical_findings": high_stale},
                evidence_ref=".aiwg/reports/stale_memory_report.json",
            ),
        ]

        result = EvolutionFlywheelDecision(
            decision=decision,
            snowball_gain_score=round(gain, 4),
            confidence=round(confidence, 4),
            blocking_reasons=blocking,
            recommended_next_phase=recommended_next_phase,
            why_this_is_the_next_lever=why,
            expected_capability_gain=expected_capability_gain,
            expected_token_efficiency_gain=expected_token_gain,
            required_tests_next=[
                "test_prompt_frame_builder",
                "test_prompt_cache_ledger",
                "test_restart_integration_gate",
                "test_context_efficiency_benchmark",
            ],
            signals=signals,
            generated_at=self._utc_now(),
        )

        if write_report:
            self.reports_root.mkdir(parents=True, exist_ok=True)
            out = self.reports_root / "evolution_flywheel_latest.json"
            out.write_text(json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8")

        return result

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")



def run_evolution_flywheel(aiwg_root: str | Path = ".aiwg", write_report: bool = True) -> EvolutionFlywheelDecision:
    runtime = EvolutionFlywheelRuntime(aiwg_root=aiwg_root)
    return runtime.run_evolution_flywheel(write_report=write_report)
