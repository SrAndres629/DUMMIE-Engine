from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class GoalClassification:
    goal_type: str
    confidence: float
    description: str

    def to_dict(self) -> dict:
        return {
            "goal_type": self.goal_type,
            "confidence": self.confidence,
            "description": self.description,
        }


@dataclass
class BusinessIntake:
    goal: str
    target_mrr: float
    current_mrr: Optional[float] = None
    ticket_price: Optional[float] = None
    customers: Optional[int] = None
    acquisition_channel: Optional[str] = None
    gross_margin: Optional[float] = None
    offer: Optional[str] = None
    operational_capacity: Optional[str] = None
    target_market: Optional[str] = None
    existing_assets: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "target_mrr": self.target_mrr,
            "current_mrr": self.current_mrr,
            "ticket_price": self.ticket_price,
            "customers": self.customers,
            "acquisition_channel": self.acquisition_channel,
            "gross_margin": self.gross_margin,
            "offer": self.offer,
            "operational_capacity": self.operational_capacity,
            "target_market": self.target_market,
            "existing_assets": self.existing_assets,
        }


@dataclass
class ToolOpportunity:
    name: str
    description: str
    opportunity_type: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "opportunity_type": self.opportunity_type,
        }


@dataclass
class GoalMemoryEntry:
    goal: str
    goal_type: str
    timestamp: str
    status: str
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "goal_type": self.goal_type,
            "timestamp": self.timestamp,
            "status": self.status,
            "metadata": self.metadata,
        }


def detect_goal_type(text: str) -> GoalClassification:
    from layers.l2_brain.goal_reasoning_runtime import GoalReasoningRuntime

    runtime = GoalReasoningRuntime()
    return runtime.classify_goal(text)


def build_business_intake(goal: str) -> BusinessIntake:
    from layers.l2_brain.goal_reasoning_runtime import GoalReasoningRuntime

    runtime = GoalReasoningRuntime()
    target = runtime.extract_target_mrr(goal)
    return BusinessIntake(goal=goal, target_mrr=target)


def generate_strategic_questions(goal: str) -> list[str]:
    from layers.l2_brain.strategic_question_generator import StrategicQuestionGenerator

    goal_type = detect_goal_type(goal).goal_type
    return StrategicQuestionGenerator().generate_questions(goal, goal_type)


def detect_tool_opportunities(goal: str) -> list[ToolOpportunity]:
    from layers.l2_brain.tool_opportunity_detector import ToolOpportunityDetector

    goal_type = detect_goal_type(goal).goal_type
    return ToolOpportunityDetector().detect_opportunities(goal, goal_type)


def create_goal_memory_entry(goal: str) -> GoalMemoryEntry:
    classification = detect_goal_type(goal)
    return GoalMemoryEntry(
        goal=goal,
        goal_type=classification.goal_type,
        timestamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        status="active",
        metadata={"confidence": classification.confidence},
    )
