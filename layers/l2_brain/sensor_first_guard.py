from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

class SensorFirstGuard:
    """
    [L2_BRAIN] Enforces the SensorFirst policy.
    Ensures that semantic retrieval is attempted before raw file reads during concept discovery.
    """
    def __init__(self, retrieval_runtime: Any = None):
        self.retrieval_runtime = retrieval_runtime

    def evaluate_request(self, request: dict, context_packet: dict | None = None) -> dict:
        """
        Evaluates a request against the SensorFirst policy.
        Returns a decision packet.
        """
        purpose = request.get("purpose", "unknown")
        action = request.get("action", "unknown")
        
        # Check for absolute blockers first
        if "secret" in str(request).lower() or "chain_of_thought" in str(request).lower() or "private reasoning" in str(request).lower():
            return {"decision": "BLOCK", "reason": "contains_secrets_or_private_reasoning"}

        # SensorFirst applies primarily to concept discovery and broad reads
        if purpose == "concept_discovery" or action == "direct_read":
            if not context_packet:
                # No retrieval context provided at all
                if request.get("justification"):
                    return {"decision": "ALLOW", "reason": "direct_read_justified"}
                else:
                    return {"decision": "WARN", "reason": "WARN_SENSOR_FIRST_REQUIRED"}

            # Context packet was provided
            status = context_packet.get("status")
            if status == "FAILED":
                 # We tried but it failed. Allow to proceed, perhaps degraded.
                 return {"decision": "ALLOW", "reason": "retrieval_failed_proceeding"}
                 
            if len(context_packet.get("results", [])) == 0:
                 return {"decision": "ALLOW", "reason": "no_semantic_hit"}
                 
            return {
                "decision": "ALLOW", 
                "reason": "semantic_context_provided", 
                "context_refs": context_packet.get("context_refs", [])
            }

        # For other purposes, allow by default
        return {"decision": "ALLOW", "reason": "purpose_exempt"}
