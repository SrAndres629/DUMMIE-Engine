import json
from pathlib import Path
from semantic_ontology_mapper import map_semantic_ontology
from mental_model_runtime import build_mental_model_for_intent
from dialectical_reasoning_runtime import run_dialectical_review
from cognitive_bias_detector import detect_cognitive_biases
from metacognitive_quality_gate import run_metacognitive_quality_gate
from metacognitive_loop_runtime import run_metacognitive_loop

def test_ontology_mapper_detects_classes_and_edges():
    intent = "decide whether DUMMIE should proceed to autonomous skill synthesis while Kuzu is degraded and tests are missing"
    res = map_semantic_ontology(intent)
    assert res["decision"] == "PASS"
    assert "UNKNOWN" not in res["classes"]
    assert len(res["ontology_graph"]["edges"]) > 0
    
    # Verify mandatory edges exist
    edges = res["ontology_graph"]["edges"]
    edge_types = [e["type"] for e in edges]
    assert "BLOCKED_BY" in edge_types or "DEGRADED_BY" in edge_types

def test_mental_model_relations_and_fields_non_empty():
    intent = "decide whether DUMMIE should proceed to autonomous skill synthesis while Kuzu is degraded and tests are missing"
    model = build_mental_model_for_intent(intent)
    
    assert len(model.relations) > 0
    assert len(model.assumptions) > 0
    assert len(model.decisions) > 0
    assert len(model.contradictions) > 0
    assert len(model.falsification_tests) > 0
    assert model.teleology["goal"] == intent

def test_dialectical_returns_repair_first():
    intent = "decide whether DUMMIE should proceed to autonomous skill synthesis while Kuzu is degraded and tests are missing"
    res = run_dialectical_review(intent)
    assert res.decision == "repair_first"
    assert "Do not proceed" in res.synthesis

def test_quality_gate_score_limits_and_rejections():
    intent = "decide whether DUMMIE should proceed to autonomous skill synthesis while Kuzu is degraded and tests are missing"
    model = build_mental_model_for_intent(intent)
    ontology = map_semantic_ontology(intent)
    
    # With degraded risks and bias report FAIL
    class DummyEpistemic:
        epistemic_debts = ["Kuzu degraded"]
        confidence = 0.5
    class DummyBias:
        decision = "FAIL"
        findings = [{"bias": "premature_scaling_bias", "message": "Failed"}]
        
    res = run_metacognitive_quality_gate(
        model=model, 
        ontology=ontology, 
        frame=None, 
        epistemic=DummyEpistemic(), 
        bias_report=DummyBias()
    )
    
    assert res.decision == "FAIL"
    assert res.quality_score <= 50.0

def test_metacognitive_loop_propagates_failures():
    intent = "decide whether DUMMIE should proceed to autonomous skill synthesis while Kuzu is degraded and tests are missing"
    res = run_metacognitive_loop(intent)
    
    assert res["decision"] == "FAIL"
    assert res["recommended_next_action"] == "repair_first"
