import json
import pytest
from pathlib import Path
from layers.l2_brain.mission_workbench import MissionWorkbenchManager

def test_mission_workbench_creation(tmp_path):
    manager = MissionWorkbenchManager(root=tmp_path)
    meta = manager.create_workbench("m1", "Goal 1")

    assert meta["mission_id"] == "m1"
    assert meta["status"] == "active"

    workbench_dir = tmp_path / "m1"
    assert (workbench_dir / "objective.md").exists()
    assert (workbench_dir / "token_budget.json").exists()
    assert (workbench_dir / "decision_log.jsonl").exists()

def test_mission_workbench_write_and_read_artifact(tmp_path):
    manager = MissionWorkbenchManager(root=tmp_path)
    manager.create_workbench("m1", "Goal 1")

    manager.write_artifact("m1", "test.txt", "content here", "note")
    read = manager.read_artifact("m1", "test.txt")

    assert read["content"] == "content here"
    assert read["name"] == "test.txt"

def test_mission_workbench_append_decision(tmp_path):
    manager = MissionWorkbenchManager(root=tmp_path)
    manager.create_workbench("m1", "Goal 1")

    decision = {
        "claim": "Requirement A",
        "evidence": ["test_fail_1"],
        "objection": "Too complex",
        "decision": "Simplify",
        "next_action": "Refactor"
    }
    manager.append_decision("m1", decision)

    log_path = tmp_path / "m1" / "decision_log.jsonl"
    lines = log_path.read_text().splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["decision"] == "Simplify"

def test_mission_workbench_finalize(tmp_path):
    manager = MissionWorkbenchManager(root=tmp_path)
    manager.create_workbench("m1", "Goal 1")

    res = manager.finalize_workbench("m1", {"status": "SUCCESS", "metrics": {"tokens": 100}})
    assert res["status"] == "finalized"
    assert res["outcome_summary"] == "SUCCESS"

    metrics_path = tmp_path / "m1" / "outcome_metrics.json"
    metrics = json.loads(metrics_path.read_text())
    assert metrics["tokens"] == 100

def test_mission_workbench_rejects_private(tmp_path):
    manager = MissionWorkbenchManager(root=tmp_path)
    manager.create_workbench("m1", "Goal 1")

    with pytest.raises(ValueError, match="private reasoning"):
        manager.write_artifact("m1", "p.txt", "chain_of_thought is secret", "note")

    with pytest.raises(ValueError, match="forbidden .env assignment"):
        manager.append_decision("m1", {"claim": "Set .env=VAL"})

def test_mission_workbench_path_traversal(tmp_path):
    manager = MissionWorkbenchManager(root=tmp_path)
    with pytest.raises(ValueError, match="path traversal"):
        manager.create_workbench("../bad", "goal")
