from cognitive_frame_builder import build_cognitive_frame
from mental_model_runtime import build_mental_model_for_intent
def test_build_frame():
    model = build_mental_model_for_intent("test")
    frame = build_cognitive_frame("test", model)
    assert frame.frame_id.startswith("frame-")
    assert frame.mental_model_refs == [model.model_id]
