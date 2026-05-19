import os
import logging

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
        if os.environ.get("DUMMIE_ALLOW_UNSAFE_BYPASS", "").lower() != "true":
            raise RuntimeError(
                "BYPASS_SHIELD_BLOCKED: UnsafeBypassShieldAdapter usage attempted "
                "without DUMMIE_ALLOW_UNSAFE_BYPASS=true"
            )
        return True, "BYPASS"

NativeShieldAdapter = UnsafeBypassShieldAdapter
