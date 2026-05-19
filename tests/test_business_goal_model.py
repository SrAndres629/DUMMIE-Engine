from __future__ import annotations

from layers.l2_brain.business_goal_model import (
    BusinessIntake,
    GoalClassification,
    GoalMemoryEntry,
    ToolOpportunity,
    create_goal_memory_entry,
    detect_goal_type,
    detect_tool_opportunities,
    generate_strategic_questions,
)


def test_models_serialization() -> None:
    gc = GoalClassification("revenue", 0.95, "desc")
    assert gc.to_dict()["goal_type"] == "revenue"

    bi = BusinessIntake("my goal", 10000.0)
    assert bi.to_dict()["target_mrr"] == 10000.0

    to = ToolOpportunity("calculator", "calc tool", "calculator")
    assert to.to_dict()["name"] == "calculator"

    gm = GoalMemoryEntry("goal", "revenue", "2026-05-19T00:00:00Z", "active")
    assert gm.to_dict()["status"] == "active"


def test_required_business_functions_exist() -> None:
    goal = "quiero facturar 10000 usd mensuales"
    cls = detect_goal_type(goal)
    assert cls.goal_type == "revenue"

    questions = generate_strategic_questions(goal)
    assert len(questions) >= 5

    opportunities = detect_tool_opportunities(goal)
    assert len(opportunities) >= 3

    entry = create_goal_memory_entry(goal)
    assert entry.goal_type == "revenue"
