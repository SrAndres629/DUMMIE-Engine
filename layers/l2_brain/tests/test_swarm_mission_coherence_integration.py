import json
import pytest
from pathlib import Path
from layers.l2_brain.mission_planner import create_mission_plan
from layers.l2_brain.mission_orchestrator_dag import build_dag_from_mission_plan
from layers.l2_brain.mission_coherence_guard import run_mission_coherence_guard
from layers.l2_brain.strategic_partner_swarm import run_strategic_partner_swarm

def test_mission_to_swarm_integration(tmp_path):
    root = tmp_path
    aiwg = root / ".aiwg"
    aiwg.mkdir()
    evo = aiwg / "evolution"
    evo.mkdir()
    repo_reports = aiwg / "reports"
    repo_reports.mkdir()
    
    current = {"current_phase": "P25"}
    seed = {
        "next_phase": "P26",
        "name": "Test Swarm Phase",
        "objective": "Test objectives",
        "required_outputs": ["layers/l2_brain/test.py"],
        "success_conditions": ["Condition 1"]
    }
    (evo / "current_position.json").write_text(json.dumps(current))
    (evo / "next_phase_seed.json").write_text(json.dumps(seed))
    
    # 1. Create Mission Plan
    plan = create_mission_plan(root=root)
    assert plan.mission_id == "MISSION_P26"
    
    # 2. Build DAG
    dag = build_dag_from_mission_plan(plan, root=root)
    assert dag.mission_id == "MISSION_P26"
    
    # 3. Run Coherence Guard
    coherence = run_mission_coherence_guard(aiwg_root=aiwg)
    assert coherence.decision == "PASS"
    
    # 4. Run Swarm
    swarm = run_strategic_partner_swarm(aiwg_root=aiwg)
    assert swarm.decision == "continue_next_phase"
    assert len(swarm.roles) == 6
