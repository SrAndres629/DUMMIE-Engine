import pytest
from layers.l2_brain.sensor_first_guard import SensorFirstGuard

def test_sfg_concept_discovery_no_retrieval():
    guard = SensorFirstGuard()
    req = {"purpose": "concept_discovery", "action": "direct_read"}
    res = guard.evaluate_request(req)
    assert res["decision"] == "WARN"
    assert res["reason"] == "WARN_SENSOR_FIRST_REQUIRED"

def test_sfg_concept_discovery_with_retrieval_hit():
    guard = SensorFirstGuard()
    req = {"purpose": "concept_discovery"}
    ctx = {"status": "READY", "results": [{"id": 1}], "context_refs": ["ref1"]}
    res = guard.evaluate_request(req, ctx)
    assert res["decision"] == "ALLOW"
    assert res["reason"] == "semantic_context_provided"
    assert "ref1" in res["context_refs"]

def test_sfg_concept_discovery_no_hit():
    guard = SensorFirstGuard()
    req = {"purpose": "concept_discovery"}
    ctx = {"status": "READY", "results": []}
    res = guard.evaluate_request(req, ctx)
    assert res["decision"] == "ALLOW"
    assert res["reason"] == "no_semantic_hit"

def test_sfg_direct_read_justified():
    guard = SensorFirstGuard()
    req = {"action": "direct_read", "justification": "line confirmation"}
    res = guard.evaluate_request(req)
    assert res["decision"] == "ALLOW"
    assert res["reason"] == "direct_read_justified"

def test_sfg_blocks_secrets():
    guard = SensorFirstGuard()
    req = {"action": "read", "query": "find my secret_key=123"}
    res = guard.evaluate_request(req)
    assert res["decision"] == "BLOCK"
    assert "contains_secrets" in res["reason"]
