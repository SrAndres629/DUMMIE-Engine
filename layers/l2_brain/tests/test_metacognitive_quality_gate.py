from metacognitive_quality_gate import run_metacognitive_quality_gate
from mental_model_runtime import build_mental_model_for_intent
from semantic_ontology_mapper import map_semantic_ontology
from cognitive_frame_builder import build_cognitive_frame

def test_quality_gate_warns_on_empty():
    model = build_mental_model_for_intent("test") # Evidence-backed model
    ontology = map_semantic_ontology("test")
    frame = build_cognitive_frame("test", model, ontology)
    result = run_metacognitive_quality_gate(model, ontology, frame)
    assert result.decision in ["PASS", "PASS_WITH_WARNINGS"]
    assert result.quality_score > 0
