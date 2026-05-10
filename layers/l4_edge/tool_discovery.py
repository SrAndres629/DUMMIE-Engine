import logging
import json
from typing import List, Any

logger = logging.getLogger("edge-discovery")

class ToolDiscovery:
    """
    [L4_EDGE] Sensor de Capacidades Real.
    Interroga al Swarm MCP y parsea dinámicamente las herramientas disponibles.
    """
    def __init__(self, mcp_gateway: Any):
        self.mcp_gateway = mcp_gateway
        self.authorized_servers = ["dummie-brain", "filesystem", "git"]

    async def get_available_capabilities(self) -> List[str]:
        """
        Descubrimiento dinámico sin hardcoding.
        """
        logger.info("L4 EDGE: Performing real-time tool discovery...")
        try:
            # Llamada real al inventario global
            response = await self.mcp_gateway.call_tool("dummie-brain", "list_all_capabilities", {})
            
            # Parsing del JSON de capacidades
            raw_text = ""
            if "result" in response and "content" in response["result"]:
                raw_text = response["result"]["content"][0].get("text", "")
            
            return self._parse_and_filter_capabilities(raw_text)
        except Exception as e:
            logger.error(f"L4 EDGE: Physical discovery failed: {e}")
            return []

    def _parse_and_filter_capabilities(self, raw_text: str) -> List[str]:
        """
        Analiza el inventario y filtra herramientas maliciosas o no autorizadas.
        """
        discovered = []
        lines = raw_text.split("\n")
        current_server = ""
        
        for line in lines:
            if line.startswith("[") and line.endswith("]:"):
                current_server = line[1:-2]
            elif current_server in self.authorized_servers and line.strip().startswith("-"):
                tool_name = line.strip()[2:].split(":")[0]
                discovered.append(f"{current_server}.{tool_name}")
        
        logger.info(f"L4 EDGE: Discovered {len(discovered)} authorized tools.")
        return discovered
