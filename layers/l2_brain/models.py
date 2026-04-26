from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional

class AuthorityLevel(Enum):
    READ = "READ"
    WRITE = "WRITE"
    ADMIN = "ADMIN"
    OWNER = "OWNER"
    HUMAN = "HUMAN"
    OVERSEER = "OVERSEER"

class IntentType(Enum):
    CONTEXT = "CONTEXT"
    FABRICATION = "FABRICATION"
    AUDIT = "AUDIT"
    REPAIR = "REPAIR"
    RESOLUTION = "RESOLUTION"
    OBSERVATION = "OBSERVATION"


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
    authority_a: AuthorityLevel = AuthorityLevel.READ
    intent_i: IntentType = IntentType.CONTEXT

    # Compact names kept for compatibility with existing code paths.
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    t: float = 0.0
    a: AuthorityLevel = AuthorityLevel.READ
    i: IntentType = IntentType.CONTEXT
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentIntent:
    # Legacy/bridge fields expected by L1 tools.
    target: str = ""
    rationale: str = ""
    risk_score: float = 0.0
    authority_a: AuthorityLevel = AuthorityLevel.READ
    intent_i: IntentType = IntentType.FABRICATION
    locus_x: str = "sw.strategy.discovery"

    # Compact fields kept for compatibility with existing code paths.
    agent_id: str = "bridge-agent"
    goal: str = ""
    intent_type: IntentType = IntentType.FABRICATION
    constraints: List[str] = field(default_factory=list)

    def __post_init__(self):
        # Keep legacy and compact fields in sync for bridge consumers.
        if not self.goal and self.rationale:
            self.goal = self.rationale
        if not self.rationale and self.goal:
            self.rationale = self.goal


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
