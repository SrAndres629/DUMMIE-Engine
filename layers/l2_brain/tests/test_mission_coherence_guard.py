import json
import pytest
from pathlib import Path
from layers.l2_brain.mission.mission_coherence_guard import MissionCoherenceGuard

@pytest.fixture
def mission_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    evo = aiwg / "evolution"
    repo = aiwg / "reports"
    evo.mkdir(parents=True)
    repo.mkdir(parents=True)
    
    current = {"current_phase": "P25"}
    seed = {"next_phase": "P26"}
    
    (evo / "current_position.json").write_text(json.dumps(current))
    (evo / "next_phase_seed.json").write_text(json.dumps(seed))
    
    return aiwg

def test_mission_guard_fail_on_p23_drift(mission_env):
    repo = mission_env / "reports"
    # Create stale P23 artifacts
    plan = {"mission_id": "MISSION_P23", "next_phase": "P23"}
    (repo / "mission_plan_latest.json").write_text(json.dumps(plan))
    
    dag = {"mission_id": "MISSION_P23"}
    (repo / "mission_orchestrator_dag_latest.json").write_text(json.dumps(dag))
    
    guard = MissionCoherenceGuard(aiwg_root=mission_env)
    report = guard.check_mission_coherence()
    
    assert report.decision == "FAIL"
    assert any("Mission ID mismatch" in f.message for f in report.findings)

def test_mission_guard_pass_on_coherent_p26(mission_env):
    repo = mission_env / "reports"
    # Create coherent P26 artifacts
    plan = {"mission_id": "MISSION_P26", "next_phase": "P26"}
    (repo / "mission_plan_latest.json").write_text(json.dumps(plan))
    
    dag = {"mission_id": "MISSION_P26", "nodes": {}}
    (repo / "mission_orchestrator_dag_latest.json").write_text(json.dumps(dag))
    
    # Create missing next node
    (repo / "next_executable_node_latest.json").write_text(json.dumps({"next_node": None}))
    
    guard = MissionCoherenceGuard(aiwg_root=mission_env)
    report = guard.check_mission_coherence()
    
    assert report.decision == "PASS"

def test_mission_guard_detects_invented_tests(mission_env):
    repo = mission_env / "reports"
    dag = {
        "mission_id": "MISSION_P26",
        "nodes": {
            "L3_1": {"tests": ["tests/test_test_module.py"]}
        }
    }
    (repo / "mission_orchestrator_dag_latest.json").write_text(json.dumps(dag))
    (repo / "mission_plan_latest.json").write_text(json.dumps({"mission_id": "MISSION_P26", "next_phase": "P26"}))
    
    guard = MissionCoherenceGuard(aiwg_root=mission_env)
    report = guard.check_mission_coherence()
    
    assert report.decision == "FAIL"
    assert any("Invented test path" in f.message for f in report.findings)
