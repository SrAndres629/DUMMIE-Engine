"""ToolSelector stub - selects MCP tools based on request."""
import logging
from typing import Any, Optional

logger = logging.getLogger("dummie.metacognition.tool_selector")

class ToolSelector:
    def __init__(self, mcp_gateway=None):
        self.mcp_gateway = mcp_gateway
        self._tools = {}
    
    def select_tools(self, query: str) -> list:
        return []
    
    def get_status(self) -> dict:
        return {"loaded": True, "tools_count": len(self._tools)}
