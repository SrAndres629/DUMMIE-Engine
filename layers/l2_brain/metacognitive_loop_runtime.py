
import json
from pathlib import Path
from mental_model_runtime import build_mental_model_for_intent
from semantic_ontology_mapper import map_semantic_ontology
from cognitive_frame_builder import build_cognitive_frame
from metacognitive_quality_gate import run_metacognitive_quality_gate
from mental_model_store import MentalModelStore

def run_metacognitive_loop(intent: str, aiwg_root: Path = Path(".aiwg")):
    store = MentalModelStore(aiwg_root.parent)
    
    # 1. Build Model
    model = build_mental_model_for_intent(intent, aiwg_root=aiwg_root)
    store.append_model(model)
    
    # 2. Map Ontology
    ontology = map_semantic_ontology(intent)
    
    # 3. Build Frame
    frame = build_cognitive_frame(intent, model, ontology)
    
    # 4. Quality Gate
    quality = run_metacognitive_quality_gate(model, ontology, frame)
    
    # Save reports
    reports = aiwg_root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    
    (reports / "mental_model_runtime_latest.json").write_text(json.dumps(model.to_dict(), indent=2))
    (reports / "semantic_ontology_map_latest.json").write_text(json.dumps(ontology, indent=2))
    (reports / "cognitive_frame_latest.json").write_text(json.dumps(frame.to_dict(), indent=2))
    (reports / "metacognitive_quality_gate_latest.json").write_text(json.dumps(quality.to_dict(), indent=2))
    
    result = {
        "decision": quality.decision,
        "intent": intent,
        "mental_model_id": model.model_id,
        "frame_id": frame.frame_id,
        "quality_gate": quality.to_dict(),
        "recommended_next_action": "respond_via_frame" if quality.decision != "FAIL" else "request_clarification",
        "dispatch_recommendation": frame.dispatch_recommendation,
        "evidence_refs": model.evidence_refs,
        "warnings": quality.warnings,
        "degraded_integrations": []
    }
    
    # Check for degraded integrations based on evidence
    if "Memory spine DEGRADED" in str(model.risks):
        result["degraded_integrations"].append("MemorySpine")
        
    (reports / "metacognitive_loop_latest.json").write_text(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    import sys
    intent = sys.argv[1] if len(sys.argv) > 1 else "plan the next refactor"
    print(json.dumps(run_metacognitive_loop(intent), indent=2))
