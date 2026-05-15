import json
import pytest
from pathlib import Path
from layers.l2_brain.phase_ledger import PhaseLedger

def test_phase_ledger_idempotency(tmp_path):
    ledger = PhaseLedger(root=tmp_path)
    ledger.create_mission("mission_idempotent", "Goal", [{"phase_id": "p1"}])
    
    event_id = "custom-evt-123"
    event = {
        "event_id": event_id,
        "event_type": "PHASE_STARTED",
        "phase_id": "p1",
        "some_data": "first"
    }
    
    res1 = ledger.append_event("mission_idempotent", event)
    
    # Try appending same event_id again with different data (should be ignored)
    event_duplicate = event.copy()
    event_duplicate["some_data"] = "second"
    res2 = ledger.append_event("mission_idempotent", event_duplicate)
    
    assert res1["event_id"] == event_id
    assert res2["event_id"] == event_id
    assert res2["some_data"] == "first" # From original
    
    events = list(ledger.iter_events("mission_idempotent"))
    # MISSION_CREATED, PHASE_REGISTERED, PHASE_STARTED
    assert len(events) == 3
    assert events[-1]["some_data"] == "first"

def test_phase_ledger_blocked_semantics(tmp_path):
    ledger = PhaseLedger(root=tmp_path)
    ledger.create_mission("mission_blocked", "Goal", [{"phase_id": "p1"}])
    
    ledger.append_event("mission_blocked", {"event_type": "PHASE_STARTED", "phase_id": "p1"})
    state_running = ledger.current_state("mission_blocked")
    assert state_running["current_phase"] == "p1"
    
    ledger.append_event("mission_blocked", {"event_type": "PHASE_BLOCKED", "phase_id": "p1", "reason": "something broke"})
    state_blocked = ledger.current_state("mission_blocked")
    
    assert state_blocked["current_phase"] == "" # Must be cleared
    assert "p1" in state_blocked["blocked_phases"]
    
    next_action = ledger.select_next_action("mission_blocked")
    assert next_action["recommended"] == "inspect_blocked_phase"
    assert next_action["phase_id"] == "p1"

def test_phase_ledger_sensitive_policy_refinement(tmp_path):
    ledger = PhaseLedger(root=tmp_path)
    ledger.create_mission("mission_sensitive", "Goal", [{"phase_id": "p1"}])
    
    # Conceptual mentions should be ALLOWED
    ledger.append_event("mission_sensitive", {
        "event_type": "PHASE_STARTED", 
        "phase_id": "p1",
        "notes": "We are discussing .env files and how to manage secrets and credentials safely."
    })
    
    # Actual assignments should be BLOCKED
    with pytest.raises(ValueError, match="forbidden .env assignment"):
        ledger.append_event("mission_sensitive", {"event_type": "PHASE_BLOCKED", "phase_id": "p1", "notes": "Set .env=ABC"})
        
    with pytest.raises(ValueError, match="forbidden secret value"):
        ledger.append_event("mission_sensitive", {"event_type": "PHASE_BLOCKED", "phase_id": "p1", "notes": "The secret is 123"})

    with pytest.raises(ValueError, match="private reasoning"):
        ledger.append_event("mission_sensitive", {"event_type": "PHASE_BLOCKED", "phase_id": "p1", "notes": "chain_of_thought: hide this"})

def test_phase_ledger_recovery_packet_quality(tmp_path):
    ledger = PhaseLedger(root=tmp_path)
    ledger.create_mission("mission_recovery", "Test recovery quality", [{"phase_id": "p1"}])
    
    ledger.append_event("mission_recovery", {"event_type": "PHASE_STARTED", "phase_id": "p1"})
    ledger.create_checkpoint("mission_recovery", "p1", {
        "evidence_refs": ["ref1"],
        "key_decisions": ["dec1"],
        "tests": {"commands": ["c1"], "passed": 1, "failed": 0}
    })
    
    ledger.generate_recovery_packet("mission_recovery")
    recovery_path = tmp_path / "mission_recovery" / "recovery_packet.md"
    content = recovery_path.read_text()
    
    assert "## Mission Goal" in content
    assert "Test recovery quality" in content
    assert "## Current Phase" in content
    assert "p1" in content
    assert "## Evidence Refs" in content
    assert "- ref1" in content
    assert "## Key Decisions" in content
    assert "- dec1" in content
    assert "## Tests Last Run" in content
    assert '"passed": 1' in content
    assert "## Next Action" in content
    assert '"recommended": "continue_phase"' in content

def test_phase_ledger_concurrency_safe(tmp_path):
    # This is a bit hard to test truly concurrently without threads/processes, 
    # but we can at least verify it doesn't crash and locks are used if fcntl is present.
    ledger = PhaseLedger(root=tmp_path)
    ledger.create_mission("mission_concurrency", "Goal", [{"phase_id": "p1"}])
    
    # Just run a few appends to ensure no obvious regression in locking logic
    for i in range(10):
        ledger.append_event("mission_concurrency", {"event_type": "PHASE_STARTED", "phase_id": "p1", "i": i})
    
    state = ledger.current_state("mission_concurrency")
    assert state["status"] == "running"
