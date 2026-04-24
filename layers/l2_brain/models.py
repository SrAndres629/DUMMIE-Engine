from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional

class AuthorityLevel(Enum):
    READ = "READ"
    WRITE = "WRITE"
    ADMIN = "ADMIN"
    OWNER = "OWNER"

class IntentType(Enum):
    CONTEXT = "CONTEXT"
    FABRICATION = "FABRICATION"
    AUDIT = "AUDIT"
    REPAIR = "REPAIR"

@dataclass
class SixDimensionalContext:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    t: float = 0.0
    a: AuthorityLevel = AuthorityLevel.READ
    i: IntentType = IntentType.CONTEXT
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentIntent:
    agent_id: str
    goal: str
    intent_type: IntentType = IntentType.FABRICATION
    constraints: List[str] = field(default_factory=list)
