import pytest
import json
from unittest.mock import MagicMock
from layers.l2_brain.action_graph import ActionNode, ActionGraph
from layers.l2_brain.domain.human_intent import classify_human_artifact, HumanIntentClassification
from layers.l2_brain.infrastructure.event_bus import AsyncEventBus
from layers.l2_brain.safe_fallbacks import FailClosedAuditor, FailClosedExecutor
from layers.l2_brain.runtime_guards import GuardInput, GuardDecision, evaluate_runtime_guards

def test_action_graph_init():
    mock_kuzu = MagicMock()
    graph = ActionGraph(kuzu_repo=mock_kuzu)
    assert graph.kuzu_repo == mock_kuzu

def test_human_intent_classification():
    res = classify_human_artifact("I think we should use a different approach.")
    assert isinstance(res, HumanIntentClassification)
    assert res.kind in ["idea", "suggestion", "decision", "experiment", "constraint", "note"]

@pytest.mark.asyncio
async def test_event_bus_simple():
    bus = AsyncEventBus()
    received = []
    def callback(payload):
        received.append(payload)
    
    bus.subscribe("test_event", callback)
    assert "test_event" in bus._subscribers

@pytest.mark.asyncio
async def test_fail_closed_auditor():
    auditor = FailClosedAuditor(reason="shield_offline")
    success, msg = await auditor.audit("<xml/>", "goal")
    assert success is False
    assert "FAIL_CLOSED" in msg

@pytest.mark.asyncio
async def test_fail_closed_executor():
    executor = FailClosedExecutor(reason="shield_offline")
    res = await executor.execute("server", "tool", {})
    assert res["error"] == "FAIL_CLOSED_EXECUTOR_UNAVAILABLE"

def test_runtime_guards_evaluation():
    inputs = GuardInput(
        provider_ready=True,
        memory_locked=False,
        parent_spec_approved=True,
        l3_policy="ALLOW"
    )
    decision = evaluate_runtime_guards(inputs)
    assert isinstance(decision, GuardDecision)
    assert decision.status == "ALLOW"
