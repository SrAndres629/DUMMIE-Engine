import json
from pathlib import Path
from mental_model_runtime import build_mental_model_for_intent
from semantic_ontology_mapper import map_semantic_ontology
from cognitive_frame_builder import build_cognitive_frame
from metacognitive_quality_gate import run_metacognitive_quality_gate
from mental_model_store import MentalModelStore
# Pack 5.2 imports
from epistemic_state_runtime import build_epistemic_state
from dialectical_reasoning_runtime import run_dialectical_review
from philosophical_ontology_runtime import build_philosophical_ontology
from cognitive_bias_detector import detect_cognitive_biases
from metacognitive_evolution_flywheel import run_metacognitive_evolution_flywheel

def run_metacognitive_loop(intent: str, aiwg_root: Path = Path(".aiwg")):
    store = MentalModelStore(aiwg_root.parent)
    reports = aiwg_root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    
    # 1. Epistemic State
    epistemic = build_epistemic_state(intent, aiwg_root=aiwg_root)
    (reports / "epistemic_state_latest.json").write_text(json.dumps(epistemic.to_dict(), indent=2))
    
    # 2. Bias Detection
    bias_report = detect_cognitive_biases(intent, aiwg_root=aiwg_root)
    (reports / "cognitive_bias_report_latest.json").write_text(json.dumps(bias_report.to_dict(), indent=2))
    
    # 3. Philosophical Ontology
    philosophical_onto = build_philosophical_ontology(intent)
    (reports / "philosophical_ontology_latest.json").write_text(json.dumps(philosophical_onto.to_dict(), indent=2))
    
    # 4. Dialectical Review
    dialectical = run_dialectical_review(intent)
    (reports / "dialectical_review_latest.json").write_text(json.dumps(dialectical.to_dict(), indent=2))
    
    # 5. Build Model
    model = build_mental_model_for_intent(intent, aiwg_root=aiwg_root)
    model.epistemic_state_ref = "epistemic_state_latest.json"
    model.dialectical_review_ref = "dialectical_review_latest.json"
    model.bias_findings = bias_report.findings
    store.append_model(model)
    
    # 6. Map Ontology (Taxonomic fallback)
    taxonomy_onto = map_semantic_ontology(intent)
    
    # 7. Build Frame
    frame = build_cognitive_frame(intent, model, taxonomy_onto)
    
    # 8. Quality Gate (Harden 5.2.1)
    quality = run_metacognitive_quality_gate(model, philosophical_onto, frame, epistemic=epistemic, bias_report=bias_report)
    
    # 9. Evolution Flywheel
    flywheel = run_metacognitive_evolution_flywheel(intent)
    (reports / "metacognitive_evolution_flywheel_latest.json").write_text(json.dumps(flywheel.to_dict(), indent=2))
    (reports / "metacognitive_evolution_delta_latest.json").write_text(json.dumps(flywheel.evolution_delta, indent=2))
    
    # Safety Propagation (Pack 5.2.1 specific rules)
    loop_decision = quality.decision
    if quality.decision == "FAIL":
        loop_decision = "FAIL"
    elif quality.decision == "NEEDS_HUMAN_REVIEW":
        loop_decision = "NEEDS_HUMAN_REVIEW"
        
    recommended_action = "respond_via_frame"
    if dialectical.decision == "repair_first":
        recommended_action = "repair_first"
    elif loop_decision == "FAIL":
        recommended_action = "request_clarification"

    # Save reports
    (reports / "mental_model_runtime_latest.json").write_text(json.dumps(model.to_dict(), indent=2))
    (reports / "semantic_ontology_map_latest.json").write_text(json.dumps(taxonomy_onto, indent=2))
    (reports / "cognitive_frame_latest.json").write_text(json.dumps(frame.to_dict(), indent=2))
    (reports / "metacognitive_quality_gate_latest.json").write_text(json.dumps(quality.to_dict(), indent=2))
    
    result = {
        "decision": loop_decision,
        "intent": intent,
        "mental_model_id": model.model_id,
        "frame_id": frame.frame_id,
        "quality_gate": quality.to_dict(),
        "epistemic_state": epistemic.to_dict(),
        "bias_report": bias_report.to_dict(),
        "philosophical_ontology": philosophical_onto.to_dict(),
        "dialectical_review": dialectical.to_dict(),
        "evolution_delta": flywheel.evolution_delta,
        "recommended_next_action": recommended_action,
        "dispatch_recommendation": frame.dispatch_recommendation,
        "warnings": quality.warnings
    }
    
    (reports / "metacognitive_loop_latest.json").write_text(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    import sys
    intent = sys.argv[1] if len(sys.argv) > 1 else "decide whether DUMMIE should proceed to autonomous skill synthesis while Kuzu is degraded and tests are missing"
    print(json.dumps(run_metacognitive_loop(intent), indent=2))
