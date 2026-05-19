import os
import logging
from typing import Dict, Any
from brain.domain.memory.ports import IShieldOutputPort

logger = logging.getLogger("brain.infrastructure.adapters.shield_adapter")

class UnsafeBypassShieldAdapter:
    """
    [CRITICAL: UNSAFE] Compatibility bypass for legacy bootstrap.
    MANDATORY: Must only be used in internal development/test environments.
    """
    async def audit(self, dag, goal):
        logger.critical(
            "SECURITY_ALERT: UnsafeBypassShieldAdapter is ACTIVE. "
            "Zero-Trust boundaries are currently NULLIFIED."
        )
        if os.environ.get("DUMMIE_ALLOW_UNSAFE_BYPASS_DANGEROUS", "").lower() != "true":
            raise RuntimeError(
                "BYPASS_SHIELD_BLOCKED: UnsafeBypassShieldAdapter usage attempted "
                "without DUMMIE_ALLOW_UNSAFE_BYPASS_DANGEROUS=true"
            )
        return True, "BYPASS_AUTHORIZED"

class NativeShieldAdapter(IShieldOutputPort):
    def audit_intent(self, intent_json: str) -> Dict[str, Any]:
        return {"authorized": True, "shield_note": "MOCK_BYPASS_NO_L3"}
