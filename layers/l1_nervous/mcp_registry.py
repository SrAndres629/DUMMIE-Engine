import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("mcp-registry")

class MCPRegistry:
    """
    [L1_NERVOUS] Registro persistente de servidores MCP y caché de herramientas.
    """
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.tool_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.load()

    def load(self):
        try:
            if not self.config_path.exists():
                logger.error(f"Registry config not found: {self.config_path}")
                return
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.servers = data.get("mcpServers", {})
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")

    def get_server_config(self, name: str) -> Optional[Dict[str, Any]]:
        return self.servers.get(name)

    def update_tools(self, name: str, tools: List[Dict[str, Any]]):
        self.tool_cache[name] = tools

    def get_tools(self, name: str) -> List[Dict[str, Any]]:
        return self.tool_cache.get(name, [])
