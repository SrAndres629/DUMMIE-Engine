import os
import logging
from typing import Dict, Any
from brain.domain.memory.ports import IShieldOutputPort

logger = logging.getLogger("brain.infrastructure.adapters.shield_adapter")

class UnsafeBypassShieldAdapter:
    """
    [DEPRECATED: UNSAFE] Bypass de compatibilidad para bootstrap antiguo.
    """
    async def audit(self, dag, goal):
        logger.warning(
            "UnsafeBypassShieldAdapter is being used. "
            "This bypasses ALL security checks."
        )
        if os.environ.get("DUMMIE_ALLOW_UNSAFE_BYPASS", "").lower() != "true":
            raise RuntimeError(
                "BYPASS_SHIELD_BLOCKED: UnsafeBypassShieldAdapter cannot be used "
                "without setting DUMMIE_ALLOW_UNSAFE_BYPASS=true"
            )
        return True, "BYPASS"

class NativeShieldAdapter(IShieldOutputPort):
    def audit_intent(self, intent_json: str) -> Dict[str, Any]:
        return {"authorized": True, "shield_note": "MOCK_BYPASS_NO_L3"}
