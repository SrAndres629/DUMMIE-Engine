from __future__ import annotations

from layers.l2_brain.business_goal_model import BusinessIntake, ToolOpportunity
from layers.l2_brain.business_goal_model import build_business_intake as _build_business_intake
from layers.l2_brain.business_goal_model import detect_tool_opportunities as _detect_tool_opportunities


def build_business_intake(goal: str) -> BusinessIntake:
    return _build_business_intake(goal)


def detect_tool_opportunities(goal: str) -> list[ToolOpportunity]:
    return _detect_tool_opportunities(goal)
