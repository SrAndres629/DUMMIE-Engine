
import json
from pathlib import Path
from mental_model_runtime import build_mental_model_for_intent
from semantic_ontology_mapper import map_semantic_ontology
from cognitive_frame_builder import build_cognitive_frame
from mental_model_store import MentalModelStore

def run_metacognitive_loop(intent: str):
    store = MentalModelStore()
    model = build_mental_model_for_intent(intent)
    store.append_model(model)
    ontology = map_semantic_ontology(intent)
    frame = build_cognitive_frame(intent, model, ontology)
    
    # Save reports
    reports = Path(".aiwg/reports")
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "mental_model_runtime_latest.json").write_text(json.dumps(model.to_dict(), indent=2))
    (reports / "semantic_ontology_map_latest.json").write_text(json.dumps(ontology, indent=2))
    (reports / "cognitive_frame_latest.json").write_text(json.dumps(frame.to_dict(), indent=2))
    
    result = {
        "decision": "PASS",
        "intent": intent,
        "mental_model_id": model.model_id,
        "frame_id": frame.frame_id,
        "recommended_next_action": "respond_via_frame",
        "dispatch_recommendation": frame.dispatch_recommendation,
        "evidence_refs": model.evidence_refs
    }
    (reports / "metacognitive_loop_latest.json").write_text(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    import sys
    intent = sys.argv[1] if len(sys.argv) > 1 else "test intent"
    print(json.dumps(run_metacognitive_loop(intent), indent=2))
