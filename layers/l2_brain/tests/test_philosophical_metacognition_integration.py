from metacognitive_loop_runtime import run_metacognitive_loop
def test_full_philosophical_loop():
    res = run_metacognitive_loop("refactor memory")
    assert "epistemic_state" in res
    assert "bias_report" in res
    assert "dialectical_review" in res
    # In degraded state, quality should reflect it
    assert res["quality_gate"]["decision"] in ["PASS_WITH_WARNINGS", "NEEDS_HUMAN_REVIEW", "FAIL"]
