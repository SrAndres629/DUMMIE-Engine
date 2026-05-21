import logging
from typing import List, Dict, Any

logger = logging.getLogger("brain.adapters.external")

try:
    from layers.l2_brain.infrastructure.ports import CodeAnalysisPort, ObservabilityPort
except ImportError:
    from ports import CodeAnalysisPort, ObservabilityPort

class UnsafeBypassShieldAdapter:
    """
    [DEPRECATED: UNSAFE] Bypass de compatibilidad para bootstrap antiguo.
    
    Este adaptador NO realiza ninguna validación de seguridad real.
    Solo se permite su uso si la variable de entorno DUMMIE_ALLOW_UNSAFE_BYPASS
    está explícitamente configurada como "true".
    """
    async def audit(self, dag, goal):
        import os
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

# [DEPRECATED ALIAS]
NativeShieldAdapter = UnsafeBypassShieldAdapter

class SocraticodeAdapter(CodeAnalysisPort):
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def analyze_symbols(self, path: str) -> List[Dict[str, Any]]:
        try:
            result = await self.proxy.call_tool("socraticode", "analyze_directory", {"path": path})
            return result.get("symbols", [])
        except Exception as e:
            logger.error(f"Error en SocraticodeAdapter: {e}")
            return []

class PhoenixAdapter(ObservabilityPort):
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def record_trace(self, session_id: str, action: str, status: str) -> None:
        try:
            await self.proxy.call_tool("phoenix", "upsert-prompt", {
                "name": f"session_{session_id}",
                "template": f"Action: {action} | Status: {status}"
            })
        except Exception as e:
            logger.error(f"Error en PhoenixAdapter: {e}")
