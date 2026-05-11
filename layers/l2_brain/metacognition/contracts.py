from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

class AuthorityLevel(str, Enum):
    A0_OBSERVER = "A0_OBSERVER"
    A1_WORKSPACE_OP = "A1_WORKSPACE_OP"
    A2_BUILDER = "A2_BUILDER"
    A3_STATION_OP = "A3_STATION_OP"
    A4_EXTERNAL_ACTOR = "A4_EXTERNAL_ACTOR"
    A5_CRITICAL_OP = "A5_CRITICAL_OP"

@dataclass
class MetacognitiveFrame:
    session_id: str
    raw_user_input: str
    refined_intent: str = ""
    strategic_objective: str = ""
    authority_level: AuthorityLevel = AuthorityLevel.A0_OBSERVER
    risk_level: str = "low"
    required_tools: List[str] = field(default_factory=list)
    missing_context: List[str] = field(default_factory=list)
    mission_plan: List[Dict[str, Any]] = field(default_factory=list)
    deliberation_summary: str = ""
    verification_findings: List[str] = field(default_factory=list)
    final_response: str = ""
    next_actions: List[str] = field(default_factory=list)
    telemetry: Dict[str, Any] = field(default_factory=dict)
