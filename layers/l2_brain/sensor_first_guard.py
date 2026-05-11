from typing import Dict, Any, Optional
from layers.l2_brain.metagateway_policy import SensorFirstPolicy, DirectReadRequest, Purpose, PolicyDecision

class SensorFirstGuard:
    """
    Runtime guard that evaluates if a direct read request complies with the Sensor-First policy.
    """
    
    def __init__(self, mode: PolicyDecision = PolicyDecision.WARN):
        self.policy = SensorFirstPolicy(mode=mode)

    def evaluate_direct_read(
        self, 
        purpose: str, 
        semantic_search_attempted: bool, 
        gateway_attempted: bool, 
        justification: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluates a direct read request.
        
        Args:
            purpose: One of 'concept_discovery', 'line_confirmation', 'debug_error', 'diff_review'.
            semantic_search_attempted: Whether semantic search was tried before this.
            gateway_attempted: Whether the Meta-Gateway was consulted before this.
            justification: Optional justification for direct read.
            
        Returns:
            A dictionary with the decision and reasoning.
        """
        try:
            purpose_enum = Purpose(purpose)
        except ValueError:
            purpose_enum = Purpose.CONCEPT_DISCOVERY # Default to most restrictive
            
        request = DirectReadRequest(
            purpose=purpose_enum,
            semantic_search_attempted=semantic_search_attempted,
            gateway_attempted=gateway_attempted,
            justification=justification
        )
        
        decision = self.policy.evaluate(request)
        
        return {
            "decision": decision.value,
            "reason": self._get_reason(decision, request),
            "mode": self.policy.mode.value,
            "should_log": True
        }

    def _get_reason(self, decision: PolicyDecision, request: DirectReadRequest) -> str:
        if decision == PolicyDecision.ALLOW:
            return "Policy satisfied: prior discovery tools were used or purpose allows direct read."
        
        if request.purpose == Purpose.CONCEPT_DISCOVERY:
            return "Sensor-First Policy Violation: Direct read attempted for concept discovery without prior semantic search or gateway consultation."
        
        if request.purpose == Purpose.LINE_CONFIRMATION:
            return "Sensor-First Policy Warning: Direct read for line confirmation without prior discovery is discouraged."
            
        return "Policy restriction applied."
