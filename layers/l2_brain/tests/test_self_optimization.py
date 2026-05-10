"""
[T10] Tests de regresión para self_optimization.py.
Verifica que:
- propose_self_optimization retorna None con pocas fallas
- propose_self_optimization retorna propuesta cuando threshold alcanzado
- SelfOptimizationProposal es frozen dataclass
- FailureSignal es frozen dataclass
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from self_optimization import (
    FailureSignal,
    SelfOptimizationProposal,
    propose_self_optimization,
)


def test_no_proposal_with_few_failures():
    """Con menos fallas que el threshold, debe retornar None."""
    failures = [
        FailureSignal(locus="L2", category="import_error"),
        FailureSignal(locus="L2", category="import_error"),
    ]
    result = propose_self_optimization(failures, threshold=3)
    assert result is None


def test_proposal_when_threshold_reached():
    """Con fallas >= threshold, debe retornar una propuesta."""
    failures = [
        FailureSignal(locus="L2", category="timeout"),
        FailureSignal(locus="L2", category="timeout"),
        FailureSignal(locus="L2", category="timeout"),
    ]
    result = propose_self_optimization(failures, threshold=3)
    assert result is not None
    assert isinstance(result, SelfOptimizationProposal)
    assert result.target_locus == "L2"
    assert result.failure_category == "timeout"
    assert result.proposed_action == "SPEC_REFACTOR"
    assert "3" in result.rationale


def test_proposal_with_mixed_categories():
    """Solo la categoría que alcanza threshold genera propuesta."""
    failures = [
        FailureSignal(locus="L1", category="crash"),
        FailureSignal(locus="L1", category="crash"),
        FailureSignal(locus="L1", category="crash"),
        FailureSignal(locus="L2", category="timeout"),
        FailureSignal(locus="L2", category="timeout"),
    ]
    result = propose_self_optimization(failures, threshold=3)
    assert result is not None
    assert result.target_locus == "L1"
    assert result.failure_category == "crash"


def test_empty_failures_returns_none():
    """Sin fallas, debe retornar None."""
    result = propose_self_optimization([], threshold=3)
    assert result is None


def test_failure_signal_is_frozen():
    """FailureSignal debe ser inmutable."""
    signal = FailureSignal(locus="L2", category="error")
    with pytest.raises(AttributeError):
        signal.locus = "L3"  # type: ignore


def test_self_optimization_proposal_is_frozen():
    """SelfOptimizationProposal debe ser inmutable."""
    proposal = SelfOptimizationProposal(
        target_locus="L2",
        failure_category="error",
        proposed_action="SPEC_REFACTOR",
        rationale="test",
    )
    with pytest.raises(AttributeError):
        proposal.target_locus = "L3"  # type: ignore
