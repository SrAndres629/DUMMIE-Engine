# Spec: 153_metacognitive_loop_runtime
# Spec: DE-V2-L2-153
"""Metacognitive Loop Runtime — Hardened for Pack 5.2.2

Before recommending next action, consults mental model truth hygiene,
evolution delta application, and self-improvement action queue to ensure
blockers are respected.
"""

import json
from pathlib import Path
from layers.l2_brain.mental_model_runtime import build_mental_model_for_intent
from layers.l2_brain.semantic_ontology_mapper import map_semantic_ontology
from layers.l2_brain.cognitive_frame_builder import build_cognitive_frame
from layers.l2_brain.metacognitive_quality_gate import run_metacognitive_quality_gate
from layers.l2_brain.mental_model_store import MentalModelStore

# Pack 5.2 imports
from layers.l2_brain.epistemic_state_runtime import build_epistemic_state
from layers.l2_brain.dialectical_reasoning_runtime import run_dialectical_review
from layers.l2_brain.philosophical_ontology_runtime import build_philosophical_ontology
from layers.l2_brain.cognitive_bias_detector import detect_cognitive_biases
from layers.l2_brain.metacognitive_evolution_flywheel import (
    run_metacognitive_evolution_flywheel,
)


def _load(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def run_metacognitive_loop(intent: str, aiwg_root: Path = Path(".aiwg")):
    store = MentalModelStore(aiwg_root.parent)
    reports = aiwg_root / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    # 1. Epistemic State
    epistemic = build_epistemic_state(intent, aiwg_root=aiwg_root)
    (reports / "epistemic_state_latest.json").write_text(
        json.dumps(epistemic.to_dict(), indent=2)
    )

    # 2. Bias Detection
    bias_report = detect_cognitive_biases(intent, aiwg_root=aiwg_root)
    (reports / "cognitive_bias_report_latest.json").write_text(
        json.dumps(bias_report.to_dict(), indent=2)
    )

    # 3. Philosophical Ontology
    philosophical_onto = build_philosophical_ontology(intent)
    (reports / "philosophical_ontology_latest.json").write_text(
        json.dumps(philosophical_onto.to_dict(), indent=2)
    )

    # 4. Dialectical Review
    dialectical = run_dialectical_review(intent)
    (reports / "dialectical_review_latest.json").write_text(
        json.dumps(dialectical.to_dict(), indent=2)
    )

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
    quality = run_metacognitive_quality_gate(
        model, philosophical_onto, frame, epistemic=epistemic, bias_report=bias_report
    )

    # 9. Evolution Flywheel
    flywheel = run_metacognitive_evolution_flywheel(intent, aiwg_root=aiwg_root)
    (reports / "metacognitive_evolution_flywheel_latest.json").write_text(
        json.dumps(flywheel.to_dict(), indent=2)
    )
    (reports / "metacognitive_evolution_delta_latest.json").write_text(
        json.dumps(flywheel.evolution_delta, indent=2)
    )

    # 10. Pack 5.2.2: Consult self-improvement blockers before recommending action
    hygiene_report = _load(reports / "mental_model_truth_hygiene_latest.json")
    delta_app = _load(reports / "evolution_delta_application_latest.json")
    si_queue = _load(reports / "self_improvement_action_queue.json")

    si_blocked = set(si_queue.get("blocked", []))
    si_blocked.update(delta_app.get("blocked_actions", []))
    si_blocked.update(flywheel.blocked_actions)

    # Safety Propagation (Pack 5.2.1 + 5.2.2 rules)
    loop_decision = quality.decision
    if quality.decision == "FAIL":
        loop_decision = "FAIL"
    elif quality.decision == "NEEDS_HUMAN_REVIEW":
        loop_decision = "NEEDS_HUMAN_REVIEW"

    recommended_action = "respond_via_frame"

    # Check if intent is autonomy/scaling and blockers exist
    is_autonomy_intent = any(
        k in intent.lower() for k in ["autonom", "synthesis", "scale", "scaling"]
    )

    if dialectical.decision == "repair_first":
        recommended_action = "repair_first"
    elif loop_decision == "FAIL":
        recommended_action = "request_clarification"
    elif is_autonomy_intent and si_blocked:
        recommended_action = "repair_first"
        if loop_decision not in ("FAIL",):
            loop_decision = "NEEDS_HUMAN_REVIEW"

    # Merge self-improvement context
    next_si_action = si_queue.get("next", flywheel.next_self_improvement_action)

    # Save reports
    (reports / "mental_model_runtime_latest.json").write_text(
        json.dumps(model.to_dict(), indent=2)
    )
    (reports / "semantic_ontology_map_latest.json").write_text(
        json.dumps(taxonomy_onto, indent=2)
    )
    (reports / "cognitive_frame_latest.json").write_text(
        json.dumps(frame.to_dict(), indent=2)
    )
    (reports / "metacognitive_quality_gate_latest.json").write_text(
        json.dumps(quality.to_dict(), indent=2)
    )

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
        "next_self_improvement_action": next_si_action,
        "self_improvement_blocked_actions": list(si_blocked),
        "dispatch_recommendation": frame.dispatch_recommendation,
        "warnings": quality.warnings,
    }

    (reports / "metacognitive_loop_latest.json").write_text(
        json.dumps(result, indent=2)
    )
    return result


if __name__ == "__main__":
    import sys

    intent = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "what should DUMMIE improve next before autonomous scaling?"
    )
    print(json.dumps(run_metacognitive_loop(intent), indent=2))
