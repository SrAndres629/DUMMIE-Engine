import pytest
from pathlib import Path
from layers.l2_brain.session_store import SessionStore
from layers.l2_brain.learning_episode import LearningEpisode

def test_session_store_append_learning_episode_idempotency(tmp_path):
    store = SessionStore(base_dir=tmp_path)
    store.create_session("s1")

    ep = LearningEpisode(
        episode_id="ep-1",
        mission_id="m1",
        session_id="s1",
        outcome="success"
    )

    path1 = store.append_learning_episode("s1", ep.to_dict())
    path2 = store.append_learning_episode("s1", ep.to_dict()) # Duplicate

    assert path1 == path2

    episodes = list(store.iter_learning_episodes("s1"))
    assert len(episodes) == 1

def test_session_store_latest_learning_episode(tmp_path):
    store = SessionStore(base_dir=tmp_path)
    store.create_session("s1")

    store.append_learning_episode("s1", {"episode_id": "ep-1", "mission_id": "m1", "outcome": "success"})
    store.append_learning_episode("s1", {"episode_id": "ep-2", "mission_id": "m2", "outcome": "failed"})

    latest = store.latest_learning_episode("s1")
    assert latest["episode_id"] == "ep-2"

def test_session_store_rejects_private_reasoning_in_episode(tmp_path):
    store = SessionStore(base_dir=tmp_path)
    store.create_session("s1")

    with pytest.raises(ValueError, match="private reasoning"):
        store.append_learning_episode("s1", {"episode_id": "ep-1", "mission_id": "m1", "action_taken": "chain-of-thought: something"})
