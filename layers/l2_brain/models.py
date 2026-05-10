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
