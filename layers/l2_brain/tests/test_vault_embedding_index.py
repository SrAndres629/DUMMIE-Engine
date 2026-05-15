import pytest
from layers.l2_brain.vault_embedding_index import VaultEmbeddingIndex

def test_vault_embedding_index_entry(tmp_path):
    idx = VaultEmbeddingIndex(root=tmp_path)
    entry = {"vault_id": "vlt-1", "content_hash": "hash1", "summary": "Note 1"}
    
    indexed = idx.index_entry(entry)
    assert indexed["vault_id"] == "vlt-1"
    assert len(indexed["vector"]) == 8
    assert (tmp_path / "vault_embedding_index.json").exists()

def test_vault_embedding_index_search(tmp_path):
    idx = VaultEmbeddingIndex(root=tmp_path)
    idx.index_entry({"vault_id": "vlt-1", "content_hash": "apple", "summary": "fruit"})
    idx.index_entry({"vault_id": "vlt-2", "content_hash": "car", "summary": "vehicle"})
    
    # Searching for "apple" should bring vlt-1 to the top
    results = idx.search_similar("apple", top_k=1)
    assert len(results) == 1
    assert results[0]["vault_id"] == "vlt-1"
    assert results[0]["score"] > 0.99
