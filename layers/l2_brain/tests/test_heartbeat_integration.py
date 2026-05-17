"""Integration tests for Heartbeat-0 metacognitive cycle."""
import json
from pathlib import Path
from heartbeat_lifecycle_runtime import run_heartbeat
from heartbeat_scheduler import HeartbeatScheduler
from heartbeat_state_store import HeartbeatStateStore


def test_full_heartbeat_integration():
    """Verify observe -> reason -> queue -> learn complete loop outputs and JSON validation."""
    # Execute actual heartbeat in observe_only mode on the real workspace
    scheduler = HeartbeatScheduler()
    res = scheduler.run_once(mode="observe_only")

    assert res["type"] == "run_once"
    assert "heartbeat_id" in res
    assert res["decision"] in ("PASS_WITH_WARNINGS", "NEEDS_HUMAN_REVIEW", "FAIL")
    assert res["dispatch_recommendation"] in ("antigravity", "codex", "local", "human_review")
    assert "next_heartbeat_seed" in res

    # Verify state store saved it
    store = HeartbeatStateStore()
    latest = store.latest_heartbeat()
    assert latest is not None
    assert latest["heartbeat_id"] == res["heartbeat_id"]

    # Verify seed written
    seed = store.load_next_seed()
    assert seed is not None
    assert seed["previous_heartbeat_id"] == res["heartbeat_id"]
    assert "next_action" in seed
