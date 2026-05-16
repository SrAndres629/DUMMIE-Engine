from mental_model_runtime import build_mental_model_for_intent
def test_build_mental_model_with_relations():
    model = build_mental_model_for_intent("refactor memory")
    assert len(model.relations) > 0
    assert "MemoryContext" in model.entities
    assert any("RefactorTarget" in str(r) for r in model.relations)
    assert model.quality_score > 0
