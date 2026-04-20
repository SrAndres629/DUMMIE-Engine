from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from brain.domain.context.models import Vector6D, AuthorityLevel

class MemoryNode(BaseModel):
    """
    Nodo de Memoria en el 4D-TES (Specs 02, 09)
    """
    id: str
    context: Vector6D
    content: str
    crystallized: bool = False
    dependencies: List[str] = Field(default_factory=list)

class SessionLedger(BaseModel):
    """
    Cognitive Memory Session Ledger (Spec 36)
    """
    session_id: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    active_nodes: List[MemoryNode] = Field(default_factory=list)
    status: str = "ACTIVE"
    authority: AuthorityLevel

class ProceduralMemory(BaseModel):
    """
    Procedural Memory Crystallization (Spec 38)
    """
    pattern_id: str
    success_rate: float
    execution_context: Dict[str, str]
    crystallized_at: datetime = Field(default_factory=datetime.utcnow)
