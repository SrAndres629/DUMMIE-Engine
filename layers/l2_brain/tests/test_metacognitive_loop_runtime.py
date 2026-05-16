from metacognitive_loop_runtime import run_metacognitive_loop
def test_metacognitive_loop():
    res = run_metacognitive_loop("test refactor")
    assert res["decision"] == "PASS"
    assert "mental_model_id" in res
