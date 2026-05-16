import json
import pytest
from pathlib import Path
from layers.l2_brain.repo_probe_runner import run_repo_probe
from layers.l2_brain.mission_planner import create_mission_plan
from layers.l2_brain.mission_orchestrator_dag import build_dag_from_mission_plan

def test_repo_to_dag_integration(tmp_path):
    root = tmp_path
    aiwg = root / ".aiwg"
    aiwg.mkdir()
    evo = aiwg / "evolution"
    evo.mkdir()
    repo_reports = aiwg / "reports"
    repo_reports.mkdir()
    
    current = {"current_phase": "P22"}
    seed = {
        "next_phase": "P23",
        "name": "Test",
        "objective": "Test obj",
        "required_outputs": ["file.py"],
        "success_conditions": []
    }
    (evo / "current_position.json").write_text(json.dumps(current))
    (evo / "next_phase_seed.json").write_text(json.dumps(seed))
    
    # Mock state coherence report
    (repo_reports / "state_coherence_guard_latest.json").write_text(json.dumps({"decision": "PASS"}))
    
    # Mock git
    import subprocess
    subprocess.run(["git", "init"], cwd=root)
    (root / "README.md").touch()
    
    # Add critical modules to avoid FAIL
    (root / "layers/l2_brain").mkdir(parents=True)
    (root / "layers/l2_brain/cli_control_plane.py").touch()
    (root / "layers/l2_brain/state_coherence_guard.py").touch()
    (root / "layers/l2_brain/embedding_adapter.py").touch()
    
    subprocess.run(["git", "add", "."], cwd=root)
    
    # Run integration
    probe = run_repo_probe(root=root)
    assert probe.decision in ["PASS", "PASS_WITH_WARNINGS"]
    
    plan = create_mission_plan(root=root)
    assert plan.mission_id == "MISSION_P23"
    
    dag = build_dag_from_mission_plan(plan, root=root)
    assert len(dag.nodes) > 0
    assert dag.decision == "PASS"
    
    # Verify latest files
    assert (repo_reports / "repo_probe_latest.json").exists()
    assert (repo_reports / "mission_plan_latest.json").exists()
    assert (repo_reports / "mission_orchestrator_dag_latest.json").exists()
    assert (repo_reports / "next_executable_node_latest.json").exists()
