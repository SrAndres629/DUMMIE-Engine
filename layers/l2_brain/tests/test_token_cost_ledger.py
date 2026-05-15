import json
import pytest
from pathlib import Path
from layers.l2_brain.token_cost_ledger import TokenCostLedger

def test_token_cost_ledger_records_and_summarizes_mission(tmp_path):
    ledger = TokenCostLedger(root=tmp_path)
    mission_id = "m1"
    
    ledger.record_usage({
        "mission_id": mission_id,
        "phase_id": "p1",
        "model_tier": "cloud_std",
        "input_tokens": 100,
        "output_tokens": 50,
        "source": "router"
    })
    
    ledger.record_usage({
        "mission_id": mission_id,
        "phase_id": "p1",
        "cached_tokens": 200,
        "output_tokens": 10,
        "source": "provider_response"
    })
    
    summary = ledger.summarize_mission(mission_id)
    assert summary["total_input_tokens"] == 100
    assert summary["total_cached_tokens"] == 200
    assert summary["total_output_tokens"] == 60
    assert summary["total_tokens"] == 360
    assert summary["event_count"] == 2
    
    ratio = ledger.cache_hit_ratio(mission_id=mission_id)
    assert ratio == 200 / 300

def test_token_cost_ledger_idempotency(tmp_path):
    ledger = TokenCostLedger(root=tmp_path)
    session_id = "s1"
    event_id = "evt1"
    
    event = {
        "session_id": session_id,
        "event_id": event_id,
        "input_tokens": 100,
        "source": "manual"
    }
    
    ledger.record_usage(event)
    ledger.record_usage(event) # Duplicate
    
    summary = ledger.summarize_session(session_id)
    assert summary["event_count"] == 1

def test_token_cost_ledger_summarize_phase(tmp_path):
    ledger = TokenCostLedger(root=tmp_path)
    mission_id = "m2"
    
    ledger.record_usage({"mission_id": mission_id, "phase_id": "p1", "input_tokens": 10})
    ledger.record_usage({"mission_id": mission_id, "phase_id": "p2", "input_tokens": 20})
    
    p1_summary = ledger.summarize_phase(mission_id, "p1")
    assert p1_summary["total_input_tokens"] == 10
    
    p2_summary = ledger.summarize_phase(mission_id, "p2")
    assert p2_summary["total_input_tokens"] == 20

def test_token_cost_ledger_rejects_private_and_secrets(tmp_path):
    ledger = TokenCostLedger(root=tmp_path)
    
    with pytest.raises(ValueError, match="private reasoning"):
        ledger.record_usage({"session_id": "s1", "notes": "chain_of_thought content"})
        
    with pytest.raises(ValueError, match="forbidden .env assignment"):
        ledger.record_usage({"session_id": "s1", "notes": ".env=SECRET"})

def test_token_cost_ledger_path_traversal(tmp_path):
    ledger = TokenCostLedger(root=tmp_path)
    with pytest.raises(ValueError, match="path traversal"):
        ledger.summarize_mission("../etc/passwd")
