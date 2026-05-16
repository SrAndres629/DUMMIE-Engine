from metacognitive_evolution_flywheel import run_metacognitive_evolution_flywheel
def test_flywheel_delta():
    res = run_metacognitive_evolution_flywheel("test")
    assert res.evolution_delta["belief_changed"]
