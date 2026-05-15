import pytest
from layers.l2_brain.memory_refs import MemoryRef

def test_memory_ref_creation():
    ref = MemoryRef(
        memory_ref_id="m1",
        ref_type="learning_episode",
        path="sessions/s1/episodes.jsonl",
        content_hash="abc",
    )
    assert ref.ref_type == "learning_episode"
    assert ref.kuzu_ready is False

def test_memory_ref_path_safety():
    with pytest.raises(ValueError, match="traversal"):
        MemoryRef(
            memory_ref_id="m1",
            ref_type="learning_episode",
            path="../sessions/s1/episodes.jsonl",
            content_hash="abc",
        )
        
    with pytest.raises(ValueError, match="relative"):
        MemoryRef(
            memory_ref_id="m1",
            ref_type="learning_episode",
            path="/absolute/sessions/s1/episodes.jsonl",
            content_hash="abc",
        )

def test_memory_ref_from_learning_episode():
    ep_data = {
        "episode_id": "ep-1",
        "mission_id": "m1",
        "session_id": "s1",
        "outcome": "success"
    }
    path = ".aiwg/sessions/s1/learning_episodes.jsonl"
    
    ref = MemoryRef.from_learning_episode(path, ep_data)
    
    assert ref.ref_type == "learning_episode"
    assert ref.path == path
    assert ref.mission_id == "m1"
    assert ref.session_id == "s1"
    assert ref.kuzu_ready is True
    assert ref.content_hash

def test_memory_ref_from_vault_entry():
    vault_data = {
        "vault_id": "vlt-1",
        "mission_id": "m1",
        "entry_type": "decision",
        "content_hash": "existing_hash"
    }
    path = ".aiwg/vault/vlt-1.json"
    
    ref = MemoryRef.from_vault_entry(path, vault_data)
    
    assert ref.ref_type == "vault_entry"
    assert ref.path == path
    assert ref.mission_id == "m1"
    assert ref.content_hash == "existing_hash"
    assert ref.kuzu_ready is True
