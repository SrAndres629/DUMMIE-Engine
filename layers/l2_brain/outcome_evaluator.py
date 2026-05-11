"""
[L2_BRAIN] Outcome Evaluator — measurable cognitive snowball feedback.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class CapabilityAmplificationResult:
    score: float
    verdict: str
    next: str
    contributions: dict[str, float] = field(default_factory=dict)


class OutcomeEvaluator:
    """Calculate capability amplification from current-vs-baseline metrics."""

    WEIGHTS: dict[str, float] = {
        "task_success_delta": 0.20,
        "token_reduction_delta": 0.15,
        "latency_reduction_delta": 0.15,
        "fewer_human_interruptions": 0.15,
        "regression_reduction": 0.15,
        "memory_reuse_gain": 0.10,
        "mentor_quality_gain": 0.10,
    }

    def calculate_capability_amplification(
        self,
        current_metrics: Mapping[str, Any],
        baseline_metrics: Mapping[str, Any] | None,
    ) -> CapabilityAmplificationResult:
        if not baseline_metrics:
            return CapabilityAmplificationResult(
                score=0,
                verdict="insufficient_baseline",
                next="collect_more_metrics",
                contributions={},
            )

        contributions = {
            "task_success_delta": _success_score(current_metrics) - _success_score(baseline_metrics),
            "token_reduction_delta": _lower_is_better_delta(
                _effective_tokens(current_metrics), _effective_tokens(baseline_metrics)
            ),
            "latency_reduction_delta": _lower_is_better_delta(
                _number(current_metrics, "latency_ms"), _number(baseline_metrics, "latency_ms")
            ),
            "fewer_human_interruptions": _lower_is_better_delta(
                _number(current_metrics, "human_interventions"), _number(baseline_metrics, "human_interventions")
            ),
            "regression_reduction": _lower_is_better_delta(
                _number(current_metrics, "regressions"), _number(baseline_metrics, "regressions")
            ),
            "memory_reuse_gain": _higher_is_better_delta(
                _number(current_metrics, "memory_reuse_gain"), _number(baseline_metrics, "memory_reuse_gain")
            ),
            "mentor_quality_gain": _higher_is_better_delta(
                _number(current_metrics, "mentor_quality_gain"), _number(baseline_metrics, "mentor_quality_gain")
            ),
        }

        weighted = sum(self.WEIGHTS[name] * contributions[name] for name in self.WEIGHTS)
        score = _clamp(weighted)
        if score > 0:
            verdict = "improved"
            next_action = "continue_collecting_metrics"
        elif score < 0:
            verdict = "regressed"
            next_action = "inspect_regression_causes"
        else:
            verdict = "neutral"
            next_action = "collect_more_metrics"

        return CapabilityAmplificationResult(
            score=score,
            verdict=verdict,
            next=next_action,
            contributions={name: _clamp(value) for name, value in contributions.items()},
        )


def _success_score(metrics: Mapping[str, Any]) -> float:
    if "task_success_delta" in metrics:
        return _clamp(_number(metrics, "task_success_delta"))
    outcome = str(metrics.get("outcome", "")).lower()
    if outcome == "success":
        return 1.0
    if outcome == "partial":
        return 0.5
    if metrics.get("tests_passed") is True:
        return 1.0
    if metrics.get("tests_passed") is False:
        return 0.0
    return _number(metrics, "task_success_rate")


def _effective_tokens(metrics: Mapping[str, Any]) -> float:
    input_tokens = _number(metrics, "input_tokens")
    cached_tokens = _number(metrics, "cached_tokens")
    output_tokens = _number(metrics, "output_tokens")
    return max(0.0, input_tokens - cached_tokens) + output_tokens


def _lower_is_better_delta(current: float, baseline: float) -> float:
    if baseline <= 0:
        return 0.0 if current <= 0 else -1.0
    return _clamp((baseline - current) / baseline)


def _higher_is_better_delta(current: float, baseline: float) -> float:
    scale = max(abs(baseline), 1.0)
    return _clamp((current - baseline) / scale)


def _number(metrics: Mapping[str, Any], key: str) -> float:
    value = metrics.get(key, 0)
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _clamp(value: float) -> float:
    return max(-1.0, min(1.0, float(value)))
