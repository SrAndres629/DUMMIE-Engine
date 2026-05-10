from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from brain.domain.context.models import SixDimensionalContext

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

class LayerCertainty(BaseModel):
    """Spec 42: Cuantifica el determinismo de una capa."""
    layer_name: str
    certainty_score: float = Field(..., ge=0.0, le=1.0)
    is_terra_incognita: bool = False
    tests_passing: int = 0
    unverified_mutations: int = 0

class OntologicalMap(BaseModel):
    """Spec 42: Mapa Ontológico del Sistema"""
    layers: Dict[str, LayerCertainty] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.now)

class DecisionRecord(BaseModel):
    """
    Decision Ledger Auditor (Spec 34)
    """
    decision_id: str
    tick: int = Field(..., description="Lamport tick of the decision")
    rationale: str
    impact_blast_radius: str
    context: SixDimensionalContext
    target_causal_hash: str
    witness_hash: str = Field(..., description="Firma criptográfica del auditor (Sentinel/PAH)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class LessonRecord(BaseModel):
    """
    Knowledge Crystallization Lesson (Spec 48)
    """
    lesson_id: str
    tick: int
    issue: str
    correction: str
    prevention: str
    context: SixDimensionalContext
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AmbiguityRecord(BaseModel):
    """
    Ambiguity Discovery (Spec 48)
    """
    ambiguity_id: str
    context: str
    resolution_plan: str
    impact_level: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SemanticConsistencyCheck(BaseModel):
    """
    Semantic Consistency Agent (Spec 39)
    """
    check_id: str
    document_uri: str
    is_consistent: bool
    violations: List[str] = Field(default_factory=list)
