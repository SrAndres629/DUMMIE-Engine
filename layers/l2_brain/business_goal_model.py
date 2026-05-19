from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class GoalClassification:
    goal_type: str  # revenue, technical, operations, strategy, unknown
    confidence: float
    description: str

    def to_dict(self) -> dict:
        return {
            "goal_type": self.goal_type,
            "confidence": self.confidence,
            "description": self.description
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
    existing_assets: List[str] = field(default_factory=list)

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
            "existing_assets": self.existing_assets
        }

@dataclass
class ToolOpportunity:
    name: str
    description: str
    opportunity_type: str  # calculator, tracker, template, etc.

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "opportunity_type": self.opportunity_type
        }

@dataclass
class GoalMemoryEntry:
    goal: str
    goal_type: str
    timestamp: str
    status: str  # active, completed, discarded
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "goal_type": self.goal_type,
            "timestamp": self.timestamp,
            "status": self.status,
            "metadata": self.metadata
        }
