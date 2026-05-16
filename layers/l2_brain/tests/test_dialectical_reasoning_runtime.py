from dialectical_reasoning_runtime import run_dialectical_review
def test_dialectical_structure():
    res = run_dialectical_review("refactor code")
    assert res.thesis
    assert res.antithesis
    assert res.synthesis
    assert res.decision == "repair_first"
