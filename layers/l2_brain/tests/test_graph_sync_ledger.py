import json
import pytest
from layers.l2_brain.graph_sync_ledger import GraphSyncLedger

def test_graph_sync_ledger_append(tmp_path):
    ledger = GraphSyncLedger(root=tmp_path)
    evt = ledger.append_event("sync-1", "GRAPH_SYNC_PLAN_CREATED", {"plan": {"nodes": []}})
    
    assert evt["sync_id"] == "sync-1"
    assert (tmp_path / "graph_sync_ledger.jsonl").exists()
    assert (tmp_path / "latest_plan.json").exists()

def test_graph_sync_ledger_list(tmp_path):
    ledger = GraphSyncLedger(root=tmp_path)
    ledger.append_event("sync-1", "NODE_READY")
    ledger.append_event("sync-2", "NODE_READY")
    
    all_evts = ledger.list_events()
    assert len(all_evts) == 2
    
    sync1_evts = ledger.list_events(sync_id="sync-1")
    assert len(sync1_evts) == 1
    assert sync1_evts[0]["sync_id"] == "sync-1"
