import pytest
from layers.l2_brain.memory_graph_runtime import MemoryGraphRuntime
from layers.l2_brain.graph_sync_ledger import GraphSyncLedger
from layers.l2_brain.vault_embedding_index import VaultEmbeddingIndex
from layers.l2_brain.kuzu_graph_sync_adapter import KuzuGraphSyncAdapter

def test_memory_graph_runtime_causal_edges(tmp_path):
    ledger = GraphSyncLedger(root=tmp_path / "graph")
    idx = VaultEmbeddingIndex(root=tmp_path / "vault")
    adapter = KuzuGraphSyncAdapter()
    
    runtime = MemoryGraphRuntime(ledger, idx, adapter)
    
    refs = [
        {
            "memory_ref_id": "r1", "content_hash": "h1", "ref_type": "learning_episode", 
            "mission_id": "m1", "vault_refs": ["r2"], "workbench_ref": "r3"
        },
        {
            "memory_ref_id": "r2", "content_hash": "h2", "ref_type": "vault_entry", "mission_id": "m1"
        },
        {
            "memory_ref_id": "r3", "content_hash": "h3", "ref_type": "workbench", "mission_id": "m1"
        }
    ]
    
    plan = runtime.build_plan_from_memory_refs(refs)
    edges = plan["edges"]
    
    # Verify PRODUCED edge (LearningEpisode -> VaultEntry)
    produced = [e for e in edges if e["edge_type"] == "PRODUCED"]
    assert len(produced) == 1
    
    # Verify SUMMARIZES edge (LearningEpisode -> Workbench)
    summarizes = [e for e in edges if e["edge_type"] == "SUMMARIZES"]
    assert len(summarizes) == 1

    # Verify DERIVED_FROM edge (VaultEntry -> Workbench)
    derived = [e for e in edges if e["edge_type"] == "DERIVED_FROM"]
    assert len(derived) == 1

def test_memory_graph_runtime_validate_drift(tmp_path):
    ledger = GraphSyncLedger(root=tmp_path / "graph")
    idx = VaultEmbeddingIndex(root=tmp_path / "vault")
    adapter = KuzuGraphSyncAdapter()
    
    class FakeCurator:
        def __init__(self, entries): self.entries = entries
        def list_entries(self): return self.entries
            
    # Case 1: No drift
    curator = FakeCurator([{"vault_id": "v1", "content_hash": "h1", "summary": "S1"}])
    idx.index_entry(curator.entries[0])
    runtime = MemoryGraphRuntime(ledger, idx, adapter, vault_curator=curator)
    
    # Create plan to populate ledger latest_plan
    refs = [{"memory_ref_id": "v1", "content_hash": "h1", "ref_type": "vault_entry"}]
    runtime.build_plan_from_memory_refs(refs)
    
    drift = runtime.validate_drift()
    assert drift["drift_detected"] is False
    
    # Case 2: Missing embedding
    curator.entries.append({"vault_id": "v2", "content_hash": "h2", "summary": "S2"})
    drift = runtime.validate_drift()
    assert drift["drift_detected"] is True
    assert "v2" in drift["missing_embedding_entries"]
    
    # Case 3: Stale hash in graph
    # (v1 still has h1 in graph plan, but we change it in curator)
    curator.entries[0]["content_hash"] = "h1-new"
    drift = runtime.validate_drift()
    assert drift["drift_detected"] is True
    assert "graph:v1" in drift["stale_hashes"]
