import logging
import os
from typing import Any, Dict

logger = logging.getLogger("mcp-driver")

class MCPDriver:
    """
    [L5_DRIVER] Adaptador de transporte MCP.
    Encapsula las llamadas al Gateway L1.
    """
    def __init__(self, mcp_gateway: Any):
        self.mcp_gateway = mcp_gateway

    async def execute(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Compatibilidad con el contrato BaseExecutor esperado por el daemon."""
        return await self.send_command(server_name, tool_name, arguments)

    async def send_command(self, server: str, tool: str, args: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"L5 DRIVER: Sending MCP command -> {server}/{tool}")
        
        # Guardia de Tipado de Rutas
        for key, value in args.items():
            if isinstance(value, str) and ("/" in value or "\\" in value):
                if os.path.exists(value):
                    if "dir" in tool.lower() and not os.path.isdir(value):
                        raise ValueError(f"TypeGuard: {value} no es un directorio válido para la herramienta {tool}")
                    if "file" in tool.lower() and not os.path.isfile(value):
                        raise ValueError(f"TypeGuard: {value} no es un archivo válido para la herramienta {tool}")

        try:
            response = await self.mcp_gateway.call_tool(
                "dummie-brain",
                "exec_remote_tool",
                {
                    "server_name": server,
                    "tool_name": tool,
                    "arguments": args
                }
            )
            # Inyección de Telemetría Cognitiva
            if isinstance(response, dict):
                response["_cognitive_telemetry"] = {
                    "payload_complexity": len(str(args)),
                    "timestamp": os.times()[4]
                }
            return response
        except Exception as e:
            logger.error(f"L5 DRIVER: Transport failure: {e}")
            return {"error": str(e)}
