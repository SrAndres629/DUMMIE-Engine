"""
Memory Domain Schemas (L2_Brain)

Este módulo define los límites transaccionales (Boundaries) de la memoria,
respetando estrictamente la Ontología Dual definida en el Anexo 09:
- 4D-TES (Tiempo/Redb): Eventos inmutables y vectores causales.
- 3D-Loci (Espacio/KùzuDB): Nodos y aristas de la topología semántica.
- 6D-Context (Absoluto): El vector cognitivo unificado.
"""

from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
import uuid


# ==========================================
# 4D-TES: MODELOS TEMPORALES (Para Redb)
# ==========================================

class VectorClock(BaseModel):
    """Reloj de Lamport para inmutabilidad topológica y resolución causal."""
    node_id: str = Field(..., description="ID del agente/nodo generador")
    tick: int = Field(..., ge=0, description="Contador monotónico local")
    timestamp: float = Field(..., description="Epoch timestamp")

class TimeEvent(BaseModel):
    """
    Delta de estado inmutable (Event Sourcing).
    Almacenado secuencialmente en Redb.
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    clock: VectorClock
    event_type: str = Field(..., description="Ej: CODE_MUTATION, RESOLUTION")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Excitación Inmutable")
    causal_parent_id: Optional[str] = Field(None, description="Enlace al evento previo en la rama causal")


# ==========================================
# 3D-LOCI: MODELOS ESPACIALES (Para KùzuDB)
# ==========================================

NodeType = Literal["Event", "Agent", "Requirement", "Ambiguity_Ticket"]
EdgeType = Literal["CAUSED_BY", "EXECUTED_BY", "VALIDATES"]

class LociNode(BaseModel):
    """Nodo en el Grafo Semántico/Espacial."""
    node_id: str = Field(..., description="ID único referenciable (ej. spec_id o event_id)")
    type: NodeType
    attributes: Dict[str, Any] = Field(default_factory=dict)
    semantic_hash: Optional[str] = Field(None, description="Para vector similarity search")

class SpatialEdge(BaseModel):
    """Arista dirigida que conecta nodos en KùzuDB."""
    source_id: str
    target_id: str
    relation: EdgeType
    properties: Dict[str, Any] = Field(default_factory=dict)


# ==========================================
# 6D-CONTEXT: MODELO UNIFICADO
# ==========================================

class CognitiveVector6D(BaseModel):
    """
    Vector V = {x, y, z, t, w, a}
    Representa el estado absoluto de un elemento en la mente del enjambre.
    """
    spatial_id: str = Field(..., description="ID en el Loci/KùzuDB (x, y, z)")
    temporal_tick: int = Field(..., description="Lamport Tick en Redb (t)")
    semantic_weight: float = Field(0.0, description="Relevancia o Entropía (w)")
    authority_level: str = Field("AGENT", description="Nivel de Soberanía (a)")
