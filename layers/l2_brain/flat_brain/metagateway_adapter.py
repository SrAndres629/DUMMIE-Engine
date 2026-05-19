import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("dummie.metagateway.adapter")

class MetaGatewayAdapter:
    """
    Adapts different MCP Gateway interfaces (call_tool vs execute_tool)
    to a unified Meta-Gateway API.
    """
    
    def __init__(self, mcp_gateway: Any):
        self.gateway = mcp_gateway

    async def _call_gateway(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if not self.gateway:
            return {"error": "gateway_not_initialized", "success": False}

        try:
            # Try call_tool (standard MCP)
            if hasattr(self.gateway, "call_tool"):
                response = await self.gateway.call_tool(server_name, tool_name, arguments)
                return self._normalize_response(response)
            
            # Try execute_tool (alternative name used in some hooks)
            if hasattr(self.gateway, "execute_tool"):
                response = await self.gateway.execute_tool(
                    server_name=server_name,
                    tool_name=tool_name,
                    arguments=arguments
                )
                return self._normalize_response(response)
                
            return {"error": "gateway_interface_unsupported", "success": False}
        except Exception as e:
            logger.error(f"Gateway call failed: {e}")
            return {"error": str(e), "success": False}

    def _normalize_response(self, response: Any) -> Dict[str, Any]:
        """Normalizes various response formats from MCP gateways."""
        if not response:
            return {"error": "empty_response", "success": False}
            
        if isinstance(response, dict):
            # If it's already normalized or has a direct result
            if "content" in response and isinstance(response["content"], list):
                # Standard MCP response with content list
                texts = [item.get("text", "") for item in response["content"] if item.get("type") == "text"]
                text_content = "\n".join(texts)
                try:
                    import json
                    parsed = json.loads(text_content)
                    return {**parsed, "success": True} if isinstance(parsed, dict) else {"result": parsed, "success": True}
                except:
                    return {"result": text_content, "success": True}
            
            if "result" in response:
                return self._normalize_response(response["result"])
                
            return {**response, "success": True}
            
        return {"result": response, "success": True}

    async def discover_capabilities(self, query: str) -> Dict[str, Any]:
        return await self._call_gateway("dummie-brain", "dummie_discover_capabilities", {"query": query})

    async def analyze_capability(self, target: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Heuristic: use a specific analyzer tool if available, or just describe
        return await self._call_gateway("dummie-brain", "dummie_analyze_capability", {"target": target, "arguments": arguments})

    async def execute_capability(self, target: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_gateway("dummie-brain", "dummie_execute_capability", {"target": target, "arguments": arguments})
