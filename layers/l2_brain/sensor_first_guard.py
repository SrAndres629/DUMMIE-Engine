from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Refined patterns for Phase 10.1
_BLOCK_PATTERNS = [
    (re.compile(r"secret\s*[:=]\s*\S+", re.I), "actual_secret_assignment"),
    (re.compile(r"token\s*[:=]\s*[a-zA-Z0-9_\-\.]{10,}", re.I), "actual_token_assignment"),
    (re.compile(r"incluye\s+tu\s+chain_of_thought", re.I), "private_reasoning_leak_request"),
    (re.compile(r"show\s+private\s+reasoning", re.I), "private_reasoning_leak_request"),
]

_CONCEPTUAL_ALLOW_PATTERNS = [
    re.compile(r"documenta\s+secret", re.I),
    re.compile(r"policy", re.I),
    re.compile(r"explica\s+qué\s+es\s+chain-of-thought", re.I),
    re.compile(r"concept", re.I),
]

class SensorFirstGuard:
    """
    [L2_BRAIN] Enforces the SensorFirst policy with precision.
    Ensures that semantic retrieval is attempted before raw file reads during concept discovery.
    """
    def __init__(self, retrieval_runtime: Any = None):
        self.retrieval_runtime = retrieval_runtime

    def evaluate_request(self, request: dict, context_packet: dict | None = None) -> dict:
        """
        Evaluates a request against the SensorFirst policy.
        """
        req_str = str(request)
        purpose = request.get("purpose", "unknown")
        action = request.get("action", "unknown")

        # 1. Hard Blockers (Actual leaks)
        for pattern, reason in _BLOCK_PATTERNS:
            if pattern.search(req_str):
                return {"decision": "BLOCK", "reason": reason}

        # 2. SensorFirst logic
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
