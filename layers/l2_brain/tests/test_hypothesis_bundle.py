import pytest
from layers.l2_brain.domain.dtos import HypothesisBundle, Hypothesis
from layers.l2_brain.domain.hypothesis_service import HypothesisService

def test_entropy_high_uncertainty():
    bundle = HypothesisBundle(
        bundle_id="b1",
        hypotheses=[
            Hypothesis(hypothesis_id="h1", content="Bug in DB", weight=1.0),
            Hypothesis(hypothesis_id="h2", content="Bug in Network", weight=1.0)
        ]
    )
    # P = [0.5, 0.5] => H(P) = 1.0
    entropy = HypothesisService.calculate_entropy(bundle)
    assert entropy == 1.0
    assert HypothesisService.should_collapse(bundle, entropy_threshold=0.5) is False

def test_entropy_low_uncertainty():
    bundle = HypothesisBundle(
        bundle_id="b2",
        hypotheses=[
            Hypothesis(hypothesis_id="h1", content="Bug in DB", weight=0.95),
            Hypothesis(hypothesis_id="h2", content="Bug in Network", weight=0.05)
        ]
    )
    # P = [0.95, 0.05] => H(P) ≈ 0.286
    entropy = HypothesisService.calculate_entropy(bundle)
    assert entropy < 0.5
    assert HypothesisService.should_collapse(bundle, entropy_threshold=0.5) is True

def test_collapse_to_dominant():
    bundle = HypothesisBundle(
        bundle_id="b3",
        hypotheses=[
            Hypothesis(hypothesis_id="h1", content="Bug in DB", weight=0.2),
            Hypothesis(hypothesis_id="h2", content="Bug in Network", weight=0.8)
        ]
    )
    dominant = HypothesisService.collapse_to_dominant(bundle)
    assert dominant is not None
    assert dominant.hypothesis_id == "h2"
