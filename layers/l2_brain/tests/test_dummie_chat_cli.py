import json
import pytest
from pathlib import Path
from layers.l2_brain.mission.dummie_chat_cli import DummieChatCli

@pytest.fixture
def chat_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    (aiwg / "reports").mkdir(parents=True)
    (aiwg / "evolution").mkdir(parents=True)
    (aiwg / "repo_intelligence").mkdir(parents=True)
    (aiwg / "heartbeat").mkdir(parents=True)
    (aiwg / "mental_models").mkdir(parents=True)
    
    (aiwg / "evolution" / "current_position.json").write_text(json.dumps({"current_phase": "P31"}))
    (aiwg / "repo_intelligence" / "repo_intelligence_manifest.json").write_text(json.dumps({"repo_id": "test"}))
    (aiwg / "repo_intelligence" / "repo_inventory.json").write_text(json.dumps({"files": []}))
    
    # Write empty models index & readiness reports for heartbeat
    (aiwg / "reports" / "self_improvement_action_queue.json").write_text(json.dumps({
        "actions": [{"action_type": "increase_test_coverage", "priority": "high", "status": "proposed"}],
        "blocked": []
    }))
    (aiwg / "reports" / "readiness_score_calibration_latest.json").write_text(json.dumps({"findings": []}))
    (aiwg / "reports" / "mental_model_truth_hygiene_latest.json").write_text(json.dumps({}))
    (aiwg / "reports" / "evolution_delta_application_latest.json").write_text(json.dumps({}))
    (aiwg / "reports" / "epistemic_state_latest.json").write_text(json.dumps({}))
    (aiwg / "reports" / "cognitive_bias_report_latest.json").write_text(json.dumps({}))
    (aiwg / "reports" / "memory_spine_entrypoint_latest.json").write_text(json.dumps({}))
    (aiwg / "reports" / "metacognitive_loop_latest.json").write_text(json.dumps({}))

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
    assert "run heartbeat" in res.answer

def test_chat_find(chat_env):
    chat = DummieChatCli(aiwg_root=chat_env)
    res = chat.handle_query("find python files")
    assert "Found 0 files" in res.answer

def test_chat_heartbeat(chat_env):
    chat = DummieChatCli(aiwg_root=chat_env)
    res = chat.handle_query("run heartbeat")
    assert "Heartbeat:" in res.answer
    assert "Selected:" in res.answer
