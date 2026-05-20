from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class PolicyDecision(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    BLOCK = "BLOCK"

class Purpose(str, Enum):
    CONCEPT_DISCOVERY = "concept_discovery"
    LINE_CONFIRMATION = "line_confirmation"
    DEBUG_ERROR = "debug_error"
    DIFF_REVIEW = "diff_review"

@dataclass
class DirectReadRequest:
    action: str = "direct_file_read"
    purpose: Purpose = Purpose.CONCEPT_DISCOVERY
    semantic_search_attempted: bool = False
    gateway_attempted: bool = False
    justification: str = ""

class SensorFirstPolicy:
    """
    Enforces the policy: discovery tools before direct file reads.
    """
    
    def __init__(self, mode: PolicyDecision = PolicyDecision.WARN):
        self.mode = mode

    def evaluate(self, request: DirectReadRequest) -> PolicyDecision:
        if request.purpose == Purpose.CONCEPT_DISCOVERY:
            if not request.semantic_search_attempted and not request.gateway_attempted:
                return self.mode # WARN or BLOCK
        
        if request.purpose == Purpose.LINE_CONFIRMATION:
            if request.gateway_attempted or request.semantic_search_attempted:
                return PolicyDecision.ALLOW
            return PolicyDecision.WARN
            
        if request.purpose in [Purpose.DEBUG_ERROR, Purpose.DIFF_REVIEW]:
            return PolicyDecision.ALLOW
            
        return PolicyDecision.ALLOW

if __name__ == "__main__":
    policy = SensorFirstPolicy(mode=PolicyDecision.WARN)
    
    # Test 1: Discovery without gateway
    req = DirectReadRequest(purpose=Purpose.CONCEPT_DISCOVERY)
    print(f"Discovery without gateway: {policy.evaluate(req)}")
    
    # Test 2: Line confirmation after gateway
    req = DirectReadRequest(purpose=Purpose.LINE_CONFIRMATION, gateway_attempted=True)
    print(f"Line confirmation after gateway: {policy.evaluate(req)}")
