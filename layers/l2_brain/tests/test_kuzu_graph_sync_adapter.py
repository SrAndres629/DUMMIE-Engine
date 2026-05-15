import pytest
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
    # Should default to dry_run if allow_write is False
    res = adapter.apply(plan, allow_write=False)
    assert res["mode"] == "dry_run"
