import time
import json
from typing import Dict, Any, List

class MetaGatewayRuntimeMeter:
    """
    Measures runtime token usage and reduction achieved via the Meta-Gateway.
    """
    
    def __init__(self):
        self.direct_read_attempts = 0
        self.sensor_first_attempts = 0
        self.gateway_attempts = 0
        self.actual_context_chars = 0
        self.policy_decisions: List[Dict[str, Any]] = []
        
        # Heuristics for comparison
        self.avg_file_tokens = 5000
        self.avg_discovery_tokens = 500
        self.avg_analysis_tokens = 800

    def record_direct_read(self, chars: int, purpose: str):
        self.direct_read_attempts += 1
        self.actual_context_chars += chars

    def record_gateway_usage(self, tool_type: str):
        self.gateway_attempts += 1
        if tool_type == "discovery":
            self.sensor_first_attempts += 1

    def record_policy_decision(self, decision: Dict[str, Any]):
        self.policy_decisions.append({
            "timestamp": time.time(),
            **decision
        })

    def get_stats(self) -> Dict[str, Any]:
        estimated_direct = self.direct_read_attempts * self.avg_file_tokens
        
        # Simplified runtime cost model
        estimated_gateway = (self.sensor_first_attempts * self.avg_discovery_tokens) + \
                            ((self.gateway_attempts - self.sensor_first_attempts) * self.avg_analysis_tokens)
        
        saved = max(0, estimated_direct - estimated_gateway)
        ratio = saved / estimated_direct if estimated_direct > 0 else 0.0
        
        return {
            "direct_read_attempts": self.direct_read_attempts,
            "sensor_first_attempts": self.sensor_first_attempts,
            "gateway_attempts": self.gateway_attempts,
            "estimated_direct_tokens": estimated_direct,
            "estimated_gateway_tokens": estimated_gateway,
            "actual_context_chars": self.actual_context_chars,
            "token_reduction_ratio": round(ratio, 4),
            "measurement_type": "runtime_heuristic",
            "confidence": "medium"
        }

    def export_report(self, path: str):
        stats = self.get_stats()
        report = {
            **stats,
            "policy_decisions": self.policy_decisions[-100:] # Last 100 decisions
        }
        with open(path, "w") as f:
            json.dump(report, f, indent=2)
