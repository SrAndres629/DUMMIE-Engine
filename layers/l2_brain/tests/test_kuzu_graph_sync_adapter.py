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
    # Should report dry_run_refused_write if allow_write is False
    res = adapter.apply(plan, allow_write=False)
    assert res["mode"] == "dry_run_refused_write"
    assert res["writes_performed"] is False

def test_kuzu_adapter_apply_simulated():
    adapter = KuzuGraphSyncAdapter()
    plan = {"sync_id": "s1", "nodes": [{"n": 1}]}
    # In this phase, even with allow_write=True, it's SIMULATED
    res = adapter.apply(plan, allow_write=True)
    if adapter.kuzu:
        assert res["status"] == "SIMULATED"
        assert res["writes_performed"] is False
        assert res["simulation"] is True
    else:
        assert res["status"] == "DEGRADED"
