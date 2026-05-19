import pytest
import os
from layers.l2_brain.kuzu_graph_sync_adapter import KuzuGraphSyncAdapter

def test_kuzu_adapter_validate():
    adapter = KuzuGraphSyncAdapter()
    plan = {"sync_id": "s1", "nodes": [{"n": 1}]}
    res = adapter.validate_plan(plan)
    assert res["valid"] is True

def test_kuzu_adapter_validate_invalid():
    adapter = KuzuGraphSyncAdapter()
    plan = {"sync_id": "s1", "blocked": True}
    res = adapter.validate_plan(plan)
    assert res["valid"] is False
    assert "blocked" in res["errors"][0]

def test_kuzu_adapter_dry_run():
    adapter = KuzuGraphSyncAdapter()
    plan = {"sync_id": "s1", "nodes": [{"n": 1}]}
    res = adapter.dry_run(plan)
    assert res["status"] == "SUCCESS"
    assert res["mode"] == "dry_run"

def test_kuzu_adapter_apply_refused():
    adapter = KuzuGraphSyncAdapter()
    plan = {"sync_id": "s1", "nodes": [{"n": 1}]}
    # Should report dry_run_refused_write if allow_write is False
    res = adapter.apply(plan, allow_write=False)
    assert res["mode"] == "dry_run_refused_write"
    assert res["writes_performed"] is False

def test_kuzu_adapter_apply_real(tmp_path):
    # Use a temp directory for physical Kuzu write testing
    db_file = str(tmp_path / "test_sync_db")
    adapter = KuzuGraphSyncAdapter(db_path=db_file)
    
    plan = {
        "sync_id": "s1",
        "nodes": [
            {
                "node_id": "node-1",
                "node_type": "LearningEpisode",
                "memory_ref_id": "ref-1",
                "mission_id": "mission-1",
                "phase_id": "phase-1",
                "content_hash": "a" * 64,
                "properties": {"test": "data"}
            }
        ],
        "edges": []
    }
    
    res = adapter.apply(plan, allow_write=True)
    if adapter.kuzu:
        assert res["status"] == "SUCCESS"
        assert res["writes_performed"] is True
        assert res["simulation"] is False
        assert res["nodes_written"] == 1
        
        # Verify node actually written using repo
        node_hash = res["id_to_hash"]["node-1"]
        node = adapter.repo.get_by_hash(node_hash)
        assert node is not None
        assert "node-1" in node.payload
    else:
        assert res["status"] == "DEGRADED"
