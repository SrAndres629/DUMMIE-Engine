import pytest
from layers.l2_brain.graph_sync_plan import GraphSyncPlan

def test_graph_sync_plan_creation():
    plan = GraphSyncPlan.create(mode="dry_run")
    assert plan.mode == "dry_run"
    assert plan.sync_id.startswith("gsp-")

def test_graph_sync_plan_add_ref():
    plan = GraphSyncPlan.create()
    ref = {
        "memory_ref_id": "mref-1",
        "content_hash": "hash1234567890",
        "ref_type": "learning_episode",
        "path": "p/1",
        "mission_id": "mission-1"
    }
    plan.add_memory_ref(ref)
    
    assert len(plan.nodes) == 1
    assert plan.nodes[0].node_type == "LearningEpisode"
    assert plan.nodes[0].node_id == "node-hash12345678"
    assert "mission-1" in plan.nodes[0].mission_id

def test_graph_sync_plan_add_edge():
    plan = GraphSyncPlan.create()
    plan.add_edge("n1", "n2", "FOLLOWS")
    
    assert len(plan.edges) == 1
    assert plan.edges[0].source == "n1"
    assert plan.edges[0].target == "n2"
    assert plan.edges[0].edge_type == "FOLLOWS"
    assert plan.edges[0].edge_id.startswith("edge-")

def test_graph_sync_plan_safety_block():
    plan = GraphSyncPlan.create()
    plan.add_edge("n1", "n2", "EVIDENCES", props={"note": "private reasoning found here"})
    assert plan.validate() is False
    assert plan.blocked is True
    assert "private reasoning" in plan.warnings[0]
