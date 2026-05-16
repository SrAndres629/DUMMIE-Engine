import json
import pytest
from pathlib import Path
from layers.l2_brain.dummie_chat_cli import DummieChatCli

@pytest.fixture
def chat_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    (aiwg / "reports").mkdir(parents=True)
    (aiwg / "evolution").mkdir(parents=True)
    (aiwg / "repo_intelligence").mkdir(parents=True)
    
    (aiwg / "evolution" / "current_position.json").write_text(json.dumps({"current_phase": "P31"}))
    (aiwg / "repo_intelligence" / "repo_intelligence_manifest.json").write_text(json.dumps({"repo_id": "test"}))
    (aiwg / "repo_intelligence" / "repo_inventory.json").write_text(json.dumps({"files": []}))
    
    return aiwg

def test_chat_status(chat_env):
    chat = DummieChatCli(aiwg_root=chat_env)
    res = chat.handle_query("status")
    assert "phase P31" in res.answer
    assert res.decision == "PASS"

def test_chat_help(chat_env):
    chat = DummieChatCli(aiwg_root=chat_env)
    res = chat.handle_query("help")
    assert "Available commands" in res.answer

def test_chat_find(chat_env):
    chat = DummieChatCli(aiwg_root=chat_env)
    res = chat.handle_query("find python files")
    assert "Found 0 files" in res.answer
