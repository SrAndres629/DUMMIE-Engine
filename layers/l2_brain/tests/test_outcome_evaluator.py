import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from outcome_evaluator import OutcomeEvaluator  # noqa: E402


def test_outcome_evaluator_calculates_positive_cas():
    result = OutcomeEvaluator().calculate_capability_amplification(
        current_metrics={
            "tests_passed": True,
            "input_tokens": 700,
            "cached_tokens": 100,
            "output_tokens": 300,
            "latency_ms": 700,
            "human_interventions": 1,
            "regressions": 0,
            "memory_reuse_gain": 0.5,
            "mentor_quality_gain": 0.25,
        },
        baseline_metrics={
            "tests_passed": False,
            "input_tokens": 1000,
            "cached_tokens": 0,
            "output_tokens": 500,
            "latency_ms": 1000,
            "human_interventions": 3,
            "regressions": 2,
            "memory_reuse_gain": 0.0,
            "mentor_quality_gain": 0.0,
        },
    )

    assert result.score > 0
    assert result.verdict == "improved"
    assert result.next == "continue_collecting_metrics"


def test_outcome_evaluator_calculates_negative_cas():
    result = OutcomeEvaluator().calculate_capability_amplification(
        current_metrics={
            "tests_passed": False,
            "input_tokens": 1600,
            "output_tokens": 900,
            "latency_ms": 1600,
            "human_interventions": 5,
            "regressions": 3,
            "memory_reuse_gain": -0.25,
            "mentor_quality_gain": -0.25,
        },
        baseline_metrics={
            "tests_passed": True,
            "input_tokens": 900,
            "output_tokens": 500,
            "latency_ms": 800,
            "human_interventions": 1,
            "regressions": 0,
            "memory_reuse_gain": 0.25,
            "mentor_quality_gain": 0.25,
        },
    )

    assert result.score < 0
    assert result.verdict == "regressed"
    assert result.next == "inspect_regression_causes"


def test_outcome_evaluator_requires_baseline_for_cas():
    result = OutcomeEvaluator().calculate_capability_amplification(
        current_metrics={"tests_passed": True},
        baseline_metrics=None,
    )

    assert result.score == 0
    assert result.verdict == "insufficient_baseline"
    assert result.next == "collect_more_metrics"
