import json
import hashlib
import logging
from mcp.server.fastmcp import FastMCP
from sdd_remote_guard import evaluate_remote_tool_admission

logger = logging.getLogger("dummie.l1.tools.gateway")

def register_gateway_tools(mcp: FastMCP, use_cases):
    proxy_manager = use_cases.proxy_manager
    orchestrator = use_cases.orchestrator

    @mcp.tool()
    async def list_remote_servers() -> str:
        """Lista los servidores MCP disponibles en el swarm."""
        return f"Servidores disponibles: {', '.join(proxy_manager.servers.keys())}"

    @mcp.tool()
    async def list_remote_tools(server_name: str) -> str:
        """Lista herramientas de un servidor proxyado."""
        try:
            tools = await proxy_manager.get_tools_for_server(server_name)
            output = [f"Herramientas en '{server_name}':"]
            for t in tools:
                output.append(f"- {t['name']}: {t.get('description', 'No desc')}")
            return "\n".join(output)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def exec_remote_tool(server_name: str, tool_name: str, arguments: dict) -> str:
        """Ejecuta una herramienta en un servidor remoto."""
        try:
            causal_id = hashlib.sha256(f"{server_name}.{tool_name}.{orchestrator.lamport_clock}".encode()).hexdigest()[:12]
            logger.info(f"Gateway [CausalID:{causal_id}]: Executing {server_name}.{tool_name}")
            admission = evaluate_remote_tool_admission(server_name, tool_name, arguments)
            if admission.status != "ALLOW":
                return f"SDD_BLOCKED: {admission.reason}"
            response = await proxy_manager.call_tool(server_name, tool_name, arguments)
            
            if "error" in response:
                err = response["error"]
                if "data" in err and "suggestion" in err["data"]:
                    return f"ERROR: {err['message']}\nSugerencia: {err['data']['suggestion']}"
                return f"Error: {json.dumps(err)}"
            
            result = response.get("result", {})
            content = result.get("content", [])
            output = [item["text"] for item in content if item.get("type") == "text"]
            return "\n".join(output) if output else "Ejecución completada."
        except Exception as e:
            return f"Fallo crítico: {str(e)}"

    @mcp.tool()
    async def search_capabilities(query: str) -> str:
        """Descubrimiento semántico de herramientas."""
        matches = []
        query_lower = query.lower()
        for s_name in proxy_manager.servers.keys():
            affinity = 50 if query_lower in s_name.lower() else 0
            if affinity > 0:
                matches.append(f"[Server] {s_name} ({affinity}%)")
                if affinity >= 80: await proxy_manager.prefetch_server(s_name)
        return "Capacidades sugeridas:\n" + "\n".join(matches) if matches else "No se encontraron capacidades."

    @mcp.tool()
    async def list_all_capabilities() -> str:
        """Inventario completo del enjambre (Vista de Dios)."""
        output = ["--- INVENTARIO GLOBAL ---"]
        for s_name in proxy_manager.servers.keys():
            try:
                tools = await proxy_manager.get_tools_for_server(s_name)
                output.append(f"\n[{s_name}]: {', '.join([t['name'] for t in tools])}")
            except:
                output.append(f"\n[{s_name}]: ERROR")
        return "\n".join(output)
