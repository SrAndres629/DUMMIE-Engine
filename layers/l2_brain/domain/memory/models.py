import hashlib
import json
from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional
from datetime import datetime
from brain.domain.context.models import SixDimensionalContext, AuthorityLevel, IntentType

class MemoryNode4DTES(BaseModel):
    """
    Nodo de Memoria Inmutable (4D-TES) - Spec 02 & Spec 36
    Alineado con el modelo físico de producción MemoryNode4D.
    """
    causal_hash: str = Field(..., description="Causal signature SHA-256")
    parent_hashes: List[str] = Field(default_factory=lambda: ["GENESIS"])
    locus_x: str
    locus_y: str
    locus_z: str
    lamport_t: int
    authority_a: str
    intent_i: str
    payload: str
    payload_hash: str
    embedding: Optional[List[float]] = Field(default_factory=lambda: [0.0])

    @property
    def parent_hash(self) -> str:
        if self.parent_hashes:
            return self.parent_hashes[0]
        return "GENESIS"

    @property
    def context(self) -> SixDimensionalContext:
        try:
            auth = AuthorityLevel(self.authority_a)
        except ValueError:
            auth = AuthorityLevel.AUTHORITY_UNSPECIFIED
        try:
            intent = IntentType(self.intent_i)
        except ValueError:
            intent = IntentType.INTENT_UNSPECIFIED
        return SixDimensionalContext(
            locus_x=self.locus_x,
            locus_y=self.locus_y,
            locus_z=self.locus_z,
            lamport_t=self.lamport_t,
            authority_a=auth,
            intent_i=intent
        )

    @classmethod
    def generate(
        cls,
        parent_hashes: Optional[List[str]] = None,
        locus_x: str = "",
        locus_y: str = "",
        locus_z: str = "",
        lamport_t: int = 0,
        authority_a: Any = "",
        intent_i: Any = "",
        payload: Any = "",
        parent_hash: Optional[str] = None,
        context: Optional[SixDimensionalContext] = None,
    ) -> "MemoryNode4DTES":
        """Factory para generar un nodo con hashes calculados determinísticamente."""
        if context is not None:
            locus_x = context.locus_x
            locus_y = context.locus_y
            locus_z = context.locus_z
            lamport_t = context.lamport_t
            authority_a = context.authority_a
            intent_i = context.intent_i
        if parent_hashes is None:
            parent_hashes = [parent_hash] if parent_hash else ["GENESIS"]
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        authority_value = authority_a.value if hasattr(authority_a, "value") else str(authority_a)
        intent_value = intent_i.value if hasattr(intent_i, "value") else str(intent_i)
        payload_hash = f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"
        
        sorted_parents = sorted(parent_hashes) if parent_hashes else ["GENESIS"]
        node_material = {
            "parent_hashes": sorted_parents,
            "payload_hash": payload_hash,
            "locus_x": locus_x,
            "locus_y": locus_y,
            "locus_z": locus_z,
            "lamport_t": lamport_t,
            "authority_a": authority_value,
            "intent_i": intent_value,
        }
        canonical = json.dumps(
            node_material,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        causal_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        return cls(
            causal_hash=causal_hash,
            parent_hashes=sorted_parents,
            locus_x=locus_x,
            locus_y=locus_y,
            locus_z=locus_z,
            lamport_t=lamport_t,
            authority_a=authority_value,
            intent_i=intent_value,
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
