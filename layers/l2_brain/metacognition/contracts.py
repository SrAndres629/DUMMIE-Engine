from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from layers.l2_brain.domain.authority import AuthorityLevel

@dataclass
class MetacognitiveFrame:
    session_id: str
    raw_user_input: str
    refined_intent: str = ""
    strategic_objective: str = ""
    authority_level: AuthorityLevel = AuthorityLevel.AGENT
    risk_level: str = "low"
    required_tools: List[str] = field(default_factory=list)
    blocked_reason: str = ""
    missing_context: List[str] = field(default_factory=list)
    mission_plan: List[Dict[str, Any]] = field(default_factory=list)
    deliberation_summary: str = ""
    verification_findings: List[str] = field(default_factory=list)
    final_response: str = ""
    next_actions: List[str] = field(default_factory=list)
    telemetry: Dict[str, Any] = field(default_factory=dict)
