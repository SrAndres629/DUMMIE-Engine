from mental_model_runtime import build_mental_model_for_intent
def test_build_mental_model():
    model = build_mental_model_for_intent("test refactor", "analysis")
    assert model.model_id.startswith("mm-")
    assert "TechnicalDebt" in model.entities
