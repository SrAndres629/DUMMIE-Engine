from epistemic_state_runtime import build_epistemic_state
def test_epistemic_state_confidence_low_on_degraded():
    res = build_epistemic_state("test")
    # Confidence should be lowered if readiness report has degraded Kuzu
    assert res.confidence < 1.0
    assert "Unresolved epistemic debt" in str(res.warnings)
