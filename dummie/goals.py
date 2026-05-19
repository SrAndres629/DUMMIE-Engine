from __future__ import annotations

from layers.l2_brain.business_goal_model import GoalClassification, GoalMemoryEntry
from layers.l2_brain.business_goal_model import create_goal_memory_entry as _create_goal_memory_entry
from layers.l2_brain.business_goal_model import detect_goal_type as _detect_goal_type
from layers.l2_brain.business_goal_model import generate_strategic_questions as _generate_strategic_questions


def detect_goal_type(text: str) -> GoalClassification:
    return _detect_goal_type(text)


def generate_strategic_questions(goal: str) -> list[str]:
    return _generate_strategic_questions(goal)


def create_goal_memory_entry(goal: str) -> GoalMemoryEntry:
    return _create_goal_memory_entry(goal)
