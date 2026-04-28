from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, Any, List, Optional

class AuthorityLevel(str, Enum):
    UNSPECIFIED = "AUTHORITY_UNSPECIFIED"
    AGENT = "AGENT"
    ENGINEER = "ENGINEER"
    ARCHITECT = "ARCHITECT"
    OVERSEER = "OVERSEER"
    HUMAN = "HUMAN"

class IntentType(str, Enum):
    UNSPECIFIED = "INTENT_UNSPECIFIED"
    OBSERVATION = "OBSERVATION"
    FABRICATION = "FABRICATION"
    MUTATION = "MUTATION"
    RESOLUTION = "RESOLUTION"
    AUDIT = "AUDIT"
    CRYSTALLIZATION = "CRYSTALLIZATION"


class MemoryTemperature(Enum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    QUARANTINED = "QUARANTINED"

@dataclass
class SixDimensionalContext:
    # Legacy/bridge names used by L1 tools.
    locus_x: str = "sw.strategy.discovery"
    locus_y: str = "L1_TRANSPORT"
    locus_z: str = "L2_BRAIN"
    lamport_t: float = 0.0
    authority_a: AuthorityLevel = AuthorityLevel.AGENT
    intent_i: IntentType = IntentType.FABRICATION

    # Compact names kept for compatibility with existing code paths.
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    t: float = 0.0
    a: AuthorityLevel = AuthorityLevel.AGENT
    i: IntentType = IntentType.FABRICATION
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentIntent:
    # Legacy/bridge fields expected by L1 tools.
    target: str = ""
    rationale: str = ""
    risk_score: float = 0.0
    authority_a: AuthorityLevel = AuthorityLevel.AGENT
    intent_i: IntentType = IntentType.MUTATION
    locus_x: str = "sw.strategy.discovery"

    # Compact fields kept for compatibility with existing code paths.
    agent_id: str = "bridge-agent"
    goal: str = ""
    intent_type: IntentType = IntentType.MUTATION
    constraints: List[str] = field(default_factory=list)

    def __post_init__(self):
        # Keep legacy and compact fields in sync for bridge consumers.
        if not self.goal and self.rationale:
            self.goal = self.rationale
        if not self.rationale and self.goal:
            self.rationale = self.goal


import hashlib
import json

class MemoryNode4D(BaseModel):
    causal_hash: str
    parent_hash: str
    locus_x: str
    locus_y: str
    locus_z: str
    lamport_t: int
    authority_a: AuthorityLevel
    intent_i: IntentType
    payload: str
    payload_hash: str
    embedding: Optional[List[float]] = Field(default_factory=lambda: [0.0])

    @property
    def context(self):
        """Propiedad de compatibilidad legacy."""
        class _LegacyContext:
            def __init__(self, node):
                self.lamport_t = node.lamport_t
                self.locus_x = node.locus_x
                self.locus_y = node.locus_y
                self.locus_z = node.locus_z
                self.authority_a = node.authority_a
                self.intent_i = node.intent_i
        return _LegacyContext(self)

    @staticmethod
    def schema_creation_query() -> str:
        return (
            "CREATE NODE TABLE MemoryNode4D("
            "causal_hash STRING, "
            "parent_hash STRING, "
            "locus_x STRING, "
            "locus_y STRING, "
            "locus_z STRING, "
            "lamport_t INT64, "
            "authority_a STRING, "
            "intent_i STRING, "
            "payload STRING, "
            "payload_hash STRING, "
            "embedding FLOAT[], "
            "PRIMARY KEY (causal_hash))"
        )

def compute_causal_hash(
    parent_hash: str,
    payload_hash: str,
    locus_x: str,
    locus_y: str,
    locus_z: str,
    lamport_t: int,
    authority_a: str,
    intent_i: str,
) -> str:
    """
    Función pura que calcula el causal_hash criptográfico utilizando un volcado JSON canónico.
    """
    import json
    import hashlib
    
    node_material = {
        "parent_hash": str(parent_hash),
        "payload_hash": str(payload_hash),
        "locus_x": str(locus_x),
        "locus_y": str(locus_y),
        "locus_z": str(locus_z),
        "lamport_t": int(lamport_t),
        "authority_a": str(authority_a),
        "intent_i": str(intent_i),
    }

    canonical = json.dumps(
        node_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

class CausalIntegrityVerifier:
    @staticmethod
    def verify_node(node: Any) -> bool:
        """
        Verifica si el causal_hash de un nodo coincide con sus propiedades.
        """
        try:
            from enum import Enum
            auth_val = node.authority_a.value if isinstance(node.authority_a, Enum) else str(node.authority_a)
            intent_val = node.intent_i.value if isinstance(node.intent_i, Enum) else str(node.intent_i)
            
            recomputed = compute_causal_hash(
                parent_hash=node.parent_hash,
                payload_hash=node.payload_hash,
                locus_x=node.locus_x,
                locus_y=node.locus_y,
                locus_z=node.locus_z,
                lamport_t=node.lamport_t,
                authority_a=auth_val,
                intent_i=intent_val
            )
            return recomputed == node.causal_hash
        except Exception:
            return False

class MemoryNode4D(BaseModel):
    # Propiedades estructurales...
    causal_hash: str
    parent_hash: str
    locus_x: str
    locus_y: str
    locus_z: str
    lamport_t: int
    authority_a: str
    intent_i: str
    payload: str
    payload_hash: str
    embedding: list[float]

    @classmethod
    def from_intent_context(
        cls,
        parent_hash: str,
        locus_x: str,
        locus_y: str,
        locus_z: str,
        lamport_t: int,
        authority_a: Any,
        intent_i: Any,
        payload: str,
    ) -> "MemoryNode4D":
        payload_hash = f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"

        from enum import Enum
        auth_val = authority_a.value if isinstance(authority_a, Enum) else str(authority_a)
        intent_val = intent_i.value if isinstance(intent_i, Enum) else str(intent_i)

        causal_hash = compute_causal_hash(
            parent_hash=parent_hash,
            payload_hash=payload_hash,
            locus_x=locus_x,
            locus_y=locus_y,
            locus_z=locus_z,
            lamport_t=lamport_t,
            authority_a=auth_val,
            intent_i=intent_val
        )

        try:
            from embedding_provider import EmbeddingProvider
        except ImportError:
            from layers.l2_brain.embedding_provider import EmbeddingProvider
        
        embedding_vec = EmbeddingProvider.generate_vector(payload)

        return cls(
            causal_hash=causal_hash,
            parent_hash=parent_hash,
            locus_x=locus_x,
            locus_y=locus_y,
            locus_z=locus_z,
            lamport_t=lamport_t,
            authority_a=auth_val,
            intent_i=intent_val,
            payload=payload,
            payload_hash=payload_hash,
            embedding=embedding_vec
        )

    def to_cypher(self) -> str:
        """
        [LEGACY BRIDGE] Serializa el nodo de memoria a Cypher delegando en cypher_codec.
        """
        try:
            from cypher_codec import node_to_create_cypher
        except ImportError:
            from layers.l2_brain.cypher_codec import node_to_create_cypher
            
        return node_to_create_cypher(self)

@dataclass
class SourceArtifact:
    provider: str
    source_uri: str
    content_type: str
    content: str
    payload_hash: str
    observed_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryTemperatureSignal:
    source_uri: str
    provider: str
    signal_type: str
    weight: float
    observed_at: str


@dataclass
class IntentDraft:
    draft_id: str
    goal: str
    risk_level: str
    proposed_steps: List[str]
    requires_human_review: bool
    target_file: str


@dataclass
class ConsensusDecision:
    consensus_id: str
    topic: str
    participants: List[str]
    decision: str
    dissent: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)


@dataclass
class RehydrationManifest:
    manifest_id: str
    source_provider: str
    scan_roots: List[str]
    artifact_kinds: List[str]
    mode: str
