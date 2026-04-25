from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

class AuthorityLevel(Enum):
    HUMAN = "HUMAN"
    OVERSEER = "OVERSEER"
    AGENT = "AGENT"

class IntentType(Enum):
    RESOLUTION = "RESOLUTION"
    OBSERVATION = "OBSERVATION"
    QUERY = "QUERY"
    FABRICATION = "FABRICATION"

@dataclass
class SixDimensionalContext:
    locus_x: str
    locus_y: str
    locus_z: str
    lamport_t: int
    authority_a: AuthorityLevel
    intent_i: IntentType
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentIntent:
    intent_type: IntentType
    target: str
    rationale: str
    risk_score: float
    authority_a: AuthorityLevel
    intent_i: IntentType
    locus_x: str
