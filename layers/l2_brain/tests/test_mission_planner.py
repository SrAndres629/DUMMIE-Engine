import json
import pytest
from pathlib import Path
from layers.l2_brain.mission_planner import MissionPlanner

@pytest.fixture
def plan_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    aiwg.mkdir()
    evo = aiwg / "evolution"
    evo.mkdir()
    repo = aiwg / "reports"
    repo.mkdir()
    
    current = {"current_phase": "P22"}
    seed = {
        "next_phase": "P23",
        "name": "Test Phase",
        "objective": "Test objective",
        "required_outputs": ["file1.py", "file2.py"],
        "success_conditions": ["Condition 1"]
    }
    
    (evo / "current_position.json").write_text(json.dumps(current))
    (evo / "next_phase_seed.json").write_text(json.dumps(seed))
    
    return tmp_path

def test_mission_planner_creates_plan(plan_env):
    planner = MissionPlanner(root=plan_env)
    plan = planner.create_mission_plan()
    
    assert plan.mission_id == "MISSION_P23"
    assert plan.objective == "Test objective"
    assert len(plan.l2_phases) == 2
    assert len(plan.l3_microphases) == 4 # 2 per L2
    assert "SDD" in str(plan.sdd_requirements)

def test_mission_planner_renders_md(plan_env):
    planner = MissionPlanner(root=plan_env)
    plan = planner.create_mission_plan()
    md = planner.render_md(plan)
    
    assert "# Mission Plan: MISSION_P23" in md
    assert "Test objective" in md
