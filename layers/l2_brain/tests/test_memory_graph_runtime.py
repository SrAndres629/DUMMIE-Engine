import pytest
from layers.l2_brain.memory_graph_runtime import MemoryGraphRuntime
from layers.l2_brain.graph_sync_ledger import GraphSyncLedger
from layers.l2_brain.vault_embedding_index import VaultEmbeddingIndex
from layers.l2_brain.kuzu_graph_sync_adapter import KuzuGraphSyncAdapter

def test_memory_graph_runtime_dry_run(tmp_path):
    ledger = GraphSyncLedger(root=tmp_path / "graph")
    idx = VaultEmbeddingIndex(root=tmp_path / "vault")
    adapter = KuzuGraphSyncAdapter()
    
    runtime = MemoryGraphRuntime(ledger, idx, adapter)
    
    refs = [
        {
            "memory_ref_id": "r1", "content_hash": "h1", "ref_type": "learning_episode", "mission_id": "m1"
        },
        {
            "memory_ref_id": "r2", "content_hash": "h2", "ref_type": "vault_entry", "mission_id": "m1"
        }
    ]
    
    res = runtime.dry_run_sync(refs)
    assert res["status"] == "SUCCESS"
    assert res["nodes_planned"] == 2
    assert res["edges_planned"] == 1
    
    # Check ledger
    events = ledger.list_events()
    assert len(events) == 2 # PLAN_CREATED and DRY_RUN_VALIDATED

def test_memory_graph_runtime_indexing_sim(tmp_path):
    ledger = GraphSyncLedger(root=tmp_path / "graph")
    idx = VaultEmbeddingIndex(root=tmp_path / "vault")
    adapter = KuzuGraphSyncAdapter()
    
    class FakeCurator:
        def list_entries(self):
            return [{"vault_id": "v1", "content_hash": "ch1", "summary": "S1"}]
            
    runtime = MemoryGraphRuntime(ledger, idx, adapter, vault_curator=FakeCurator())
    
    res = runtime.index_vault_entries()
    assert res["status"] == "SUCCESS"
    assert res["indexed_count"] == 1
    
    # Check embedding index
    indexed = idx.search_similar("test")
    assert len(indexed) == 1
