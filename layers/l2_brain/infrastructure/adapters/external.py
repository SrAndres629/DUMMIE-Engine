import logging
from typing import List, Dict, Any

logger = logging.getLogger("brain.adapters.external")

class NativeShieldAdapter:
    async def audit(self, dag, goal):
        return True, "BYPASS"

class SocraticodeAdapter:
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def analyze_symbols(self, path: str) -> List[Dict[str, Any]]:
        try:
            result = await self.proxy.call_tool("socraticode", "analyze_directory", {"path": path})
            return result.get("symbols", [])
        except Exception as e:
            logger.error(f"Error en SocraticodeAdapter: {e}")
            return []

class PhoenixAdapter:
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
