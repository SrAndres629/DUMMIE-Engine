"""Tests for heartbeat_state_store.py — Heartbeat-0"""
import json, tempfile, shutil
from pathlib import Path
from heartbeat_state_store import HeartbeatStateStore


def test_idempotent_append():
    tmp = Path(tempfile.mkdtemp())
    try:
        store = HeartbeatStateStore(aiwg_root=tmp / ".aiwg")
        hb = {"heartbeat_id": "hb-test1", "mode": "observe_only", "decision": "PASS", "created_at": "2026-05-16"}
        store.append_heartbeat(hb)
        store.append_heartbeat(hb)  # second write

        entries = list(store.iter_beats() if hasattr(store, "iter_beats") else store.iter_heartbeats())
        assert len(entries) == 1
    finally:
        shutil.rmtree(tmp)


def test_latest_and_seed():
    tmp = Path(tempfile.mkdtemp())
    try:
        store = HeartbeatStateStore(aiwg_root=tmp / ".aiwg")
        hb = {"heartbeat_id": "hb-test2", "mode": "advisory", "decision": "PASS_WITH_WARNINGS", "created_at": "2026-05-16"}
        store.append_heartbeat(hb)
        latest = store.latest_heartbeat()
        assert latest is not None
        assert latest["heartbeat_id"] == "hb-test2"

        seed = {"previous_heartbeat_id": "hb-test2", "next_action": "repair_kuzu"}
        store.write_next_seed(seed)
        loaded = store.load_next_seed()
        assert loaded["next_action"] == "repair_kuzu"
    finally:
        shutil.rmtree(tmp)


def test_index_written():
    tmp = Path(tempfile.mkdtemp())
    try:
        store = HeartbeatStateStore(aiwg_root=tmp / ".aiwg")
        hb = {"heartbeat_id": "hb-test3", "mode": "observe_only", "decision": "PASS", "created_at": "2026-05-16"}
        store.append_heartbeat(hb)
        index = json.loads((tmp / ".aiwg" / "heartbeat" / "heartbeat_index.json").read_text())
        assert "hb-test3" in index
    finally:
        shutil.rmtree(tmp)
