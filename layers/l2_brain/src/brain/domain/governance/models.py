from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class KaizenLoop(BaseModel):
    """
    Kaizen Loop Refinement (Spec 27)
    """
    loop_id: str
    target_metric: str
    current_value: float
    target_value: float
    iterations: int = 0

class ImpactAnalysis(BaseModel):
    """
    Impact Analytics & Blast Radius (Spec 31)
    """
    analysis_id: str
    target_component: str
    blast_radius: List[str]
    risk_level: str

class DecisionRecord(BaseModel):
    """
    Decision Ledger Auditor (Spec 34)
    """
    decision_id: str
    rationale: str
    impact: ImpactAnalysis
    approved_by: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SemanticConsistencyCheck(BaseModel):
    """
    Semantic Consistency Agent (Spec 39)
    """
    check_id: str
    document_uri: str
    is_consistent: bool
    violations: List[str] = Field(default_factory=list)
