from metacognitive_loop_runtime import run_metacognitive_loop
def test_metacognitive_loop_quality():
    res = run_metacognitive_loop("refactor memory")
    assert "quality_gate" in res
    # Valid decisions in degraded state
    assert res["decision"] in ["PASS_WITH_WARNINGS", "NEEDS_HUMAN_REVIEW", "FAIL"]
