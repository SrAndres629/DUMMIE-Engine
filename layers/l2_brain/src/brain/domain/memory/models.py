import hashlib
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from brain.domain.context.models import SixDimensionalContext, AuthorityLevel

class MemoryNode4DTES(BaseModel):
    """
    Nodo de Memoria Inmutable (4D-TES) - Spec 02
    """
    causal_hash: str = Field(..., description="SHA-256(parent_hash + payload_hash + 6d_context)")
    parent_hash: str = Field(..., description="Puntero criptográfico al nodo anterior")
    context: SixDimensionalContext
    payload: bytes = Field(..., description="Excitación inmutable (Zstd compressed JSON o AST)")
    payload_hash: str = Field(..., description="Hash del payload aislado")

    @classmethod
    def generate(cls, parent_hash: str, context: SixDimensionalContext, payload: bytes) -> "MemoryNode4DTES":
        """Factory para generar un nodo con hashes calculados."""
        payload_hash = hashlib.sha256(payload).hexdigest()
        context_hash = context.compute_context_hash()
        
        causal_seed = f"{parent_hash}{payload_hash}{context_hash}"
        causal_hash = hashlib.sha256(causal_seed.encode('utf-8')).hexdigest()
        
        return cls(
            causal_hash=causal_hash,
            parent_hash=parent_hash,
            context=context,
            payload=payload,
            payload_hash=payload_hash
        )

class SessionLedger(BaseModel):
    """
    Cognitive Memory Session Ledger (Spec 36)
    """
    session_id: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    active_nodes: List[MemoryNode4DTES] = Field(default_factory=list)
    status: str = "ACTIVE"
    authority: AuthorityLevel

class EgoState(BaseModel):
    """
    Estado Efímero del Ego en el Ledger de Sesión (Spec 36)
    """
    agent_id: str
    tick: int = Field(..., description="Lamport tick")
    thought_vector: str = Field(..., description="Representación latente o descripción")
    action: str = Field(..., description="Intención física o llamada a herramienta")
    context: SixDimensionalContext

class CrystallizedSkill(BaseModel):
    """
    Habilidad destilada con proveniencia causal inquebrantable (Spec 38)
    """
    skill_id: str
    yaml_payload: str = Field(..., description="El contrato YAML ejecutable")
    source_causal_hashes: List[str] = Field(default_factory=list, description="Nodos 4D-TES que originaron el aprendizaje")
    skill_hash: str = Field(..., description="Firma criptográfica que previene tampering")
