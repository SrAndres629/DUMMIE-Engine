import pytest
from layers.l2_brain.mission.mission_orchestrator_dag import MissionOrchestratorDAG, DAGNode

@pytest.fixture
def mock_plan():
    class Phase:
        def __init__(self, pid, title, out):
            self.phase_id = pid
            self.title = title
            self.outputs = out

    class Micro:
        def __init__(self, mid, pid, title, act, out, t):
            self.microphase_id = mid
            self.parent_phase_id = pid
            self.title = title
            self.action = act
            self.expected_file_changes = out
            self.tests_to_run = t

    class Plan:
        def __init__(self):
            self.mission_id = "TEST_MISSION"
            self.l2_phases = [Phase("L2_1", "Phase 1", ["f1.py"])]
            self.l3_microphases = [
                Micro("L2_1_M1", "L2_1", "Draft f1", "draft", ["f1.py"], []),
                Micro("L2_1_M2", "L2_1", "Verify f1", "verify", [], ["test_f1.py"])
            ]
    return Plan()

def test_dag_building(mock_plan):
    orchestrator = MissionOrchestratorDAG()
    dag = orchestrator.build_dag_from_mission_plan(mock_plan)
    
    assert dag.mission_id == "TEST_MISSION"
    assert "START" in dag.nodes
    assert "L2_1" in dag.nodes
    assert "L2_1_M1" in dag.nodes
    assert "L2_1_M2" in dag.nodes
    assert "END" in dag.nodes
    
    # Check dependencies
    assert "START" in dag.nodes["L2_1_M1"].depends_on
    assert "L2_1_M1" in dag.nodes["L2_1_M2"].depends_on
    assert "L2_1_M2" in dag.nodes["L2_1"].depends_on

def test_cycle_detection():
    orchestrator = MissionOrchestratorDAG()
    class Dag:
        def __init__(self):
            self.nodes = {
                "A": DAGNode("A", "L2", "A", depends_on=["B"]),
                "B": DAGNode("B", "L2", "B", depends_on=["A"])
            }
    dag = Dag()
    assert orchestrator._has_cycle(dag) == True

def test_next_executable_node(mock_plan):
    orchestrator = MissionOrchestratorDAG()
    dag = orchestrator.build_dag_from_mission_plan(mock_plan)
    
    # START is ready
    node = orchestrator.select_next_executable_node(dag)
    assert node.node_id == "START"
    
    # Mark START as done
    dag.nodes["START"].status = "done"
    node = orchestrator.select_next_executable_node(dag)
    assert node.node_id == "L2_1_M1"
