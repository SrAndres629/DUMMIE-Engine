import json
import logging
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
from application.use_cases import BrainToolUseCases
from tools_impl.core import register_core_tools
from tools_impl.swarm import register_swarm_tools
from tools_impl.nervous import register_nervous_tools
from tools_impl.knowledge import register_knowledge_tools
from tools_impl.sdd import register_sdd_tools

logger = logging.getLogger("dummie-mcp.tools")

def register_tools(mcp: FastMCP, orchestrator, proxy_manager, root_dir: str):
    """Dispatcher para el registro de herramientas (Arquitectura Hexagonal)."""
    
    logger.info("Iniciando registro de herramientas Meta-Gateway (L1-Hexagonal)...")
    
    # Capa de Aplicación
    use_cases = BrainToolUseCases(orchestrator, proxy_manager)

    # 1. Instancia interna para encapsular TODAS las herramientas nativas
    internal_mcp = FastMCP("Internal-Registry")

    # Registro por Dominio en el registry interno (NO en el público)
    register_core_tools(internal_mcp, use_cases, root_dir)
    register_swarm_tools(internal_mcp, use_cases, root_dir)
    register_nervous_tools(internal_mcp, use_cases, root_dir)
    register_knowledge_tools(internal_mcp, use_cases)
    register_sdd_tools(internal_mcp, use_cases)
    
    # NOTA: Desactivamos register_gateway_tools porque el Meta-Gateway absorbe su funcionalidad.

    # 2. Exponer las 3 herramientas maestras (Meta-Gateway) en el MCP público
    
    @mcp.tool()
    async def dummie_discover_capabilities(query: str = "") -> str:
        """
        Descubre las capacidades disponibles en el sistema (locales y remotas).
        Si no sabes qué herramientas tienes, ejecuta esta primero.
        """
        output = ["=== CAPACIDADES LOCALES (Dummie Brain) ==="]
        local_tools = internal_mcp._tool_manager.list_tools()
        for t in local_tools:
            if query.lower() in t.name.lower() or query.lower() in t.description.lower():
                output.append(f"- local.{t.name}: {t.description}")
        
        output.append("\n=== CAPACIDADES REMOTAS (Proxy Servers) ===")
        try:
            for s_name in proxy_manager.servers.keys():
                if query and query.lower() not in s_name.lower():
                    # Si hay query, hacemos pre-fetch solo si el servidor coincide con la busqueda.
                    # Sino, listamos todos los servidores y sus tools.
                    pass
                
                try:
                    r_tools = await proxy_manager.get_tools_for_server(s_name)
                    output.append(f"\n[{s_name}]:")
                    for t in r_tools:
                        name = t.get('name', 'unknown')
                        desc = t.get('description', 'No description')
                        if query.lower() in name.lower() or query.lower() in desc.lower():
                            output.append(f"- {s_name}.{name}: {desc}")
                except Exception as e:
                    output.append(f"[{s_name}]: Offline o Error de handshake ({e})")
        except Exception as e:
            output.append(f"Error cargando servidores remotos: {e}")
            
        return "\n".join(output)

    @mcp.tool()
    async def dummie_analyze_capability(target: str) -> str:
        """
        Analiza una capacidad específica para obtener sus argumentos y JSON Schema.
        Ejemplo target: 'local.crystallize' o 'git.git_status'
        """
        if target.startswith("local."):
            name = target.split("local.", 1)[1]
            local_tools = internal_mcp._tool_manager.list_tools()
            for t in local_tools:
                if t.name == name:
                    return f"SCHEMA PARA '{target}':\n{json.dumps(t.parameters, indent=2)}"
            return f"Error: Capacidad local '{name}' no encontrada."
        else:
            # Remote capability
            if "." not in target:
                return "Error: Target remoto debe tener el formato 'server.tool_name' (ej. 'git.git_status')"
            server_name, tool_name = target.split(".", 1)
            try:
                r_tools = await proxy_manager.get_tools_for_server(server_name)
                for t in r_tools:
                    if t.get("name") == tool_name:
                        schema = t.get("inputSchema", {})
                        return f"SCHEMA PARA '{target}':\n{json.dumps(schema, indent=2)}"
                return f"Error: Herramienta '{tool_name}' no encontrada en el servidor '{server_name}'."
            except Exception as e:
                return f"Error conectando con el servidor '{server_name}': {e}"

    @mcp.tool()
    async def dummie_execute_capability(target: str, arguments: Dict[str, Any]) -> str:
        """
        Ejecuta una capacidad local o remota bajo SDD Guardrails.
        Debes pasar los argumentos exactamente como los indica el schema.
        """
        logger.info(f"META-GATEWAY EXECUTION: {target}")
        
        if target.startswith("local."):
            name = target.split("local.", 1)[1]
            local_tools = internal_mcp._tool_manager.list_tools()
            for t in local_tools:
                if t.name == name:
                    try:
                        # Ejecutar la función Python subyacente con validación Pydantic
                        res = await t.run(arguments)
                        return str(res)
                    except Exception as e:
                        return f"Error interno ejecutando '{target}': {e}"
            return f"Error: Capacidad local '{name}' no encontrada."
        else:
            # Remote capability
            if "." not in target:
                return "Error: Target remoto debe tener el formato 'server.tool_name'"
            server_name, tool_name = target.split(".", 1)
            try:
                from sdd_remote_guard import evaluate_remote_tool_admission
                import hashlib
                causal_id = hashlib.sha256(f"{server_name}.{tool_name}.{orchestrator.lamport_clock}".encode()).hexdigest()[:12]
                logger.info(f"Meta-Gateway Proxy [CausalID:{causal_id}]: {server_name}.{tool_name}")
                
                admission = evaluate_remote_tool_admission(server_name, tool_name, arguments)
                if admission.status != "ALLOW":
                    return f"SDD_BLOCKED: {admission.reason}"
                
                response = await proxy_manager.call_tool(server_name, tool_name, arguments)
                
                if isinstance(response, dict) and "error" in response:
                    err = response["error"]
                    if "data" in err and "suggestion" in err["data"]:
                        return f"ERROR: {err.get('message', '')}\nSugerencia: {err['data']['suggestion']}"
                    return f"Error: {json.dumps(err)}"
                
                result = response.get("result", {}) if isinstance(response, dict) else response
                if isinstance(result, dict) and "content" in result:
                    content = result.get("content", [])
                    output = [item["text"] for item in content if item.get("type") == "text"]
                    return "\n".join(output) if output else "Ejecución completada."
                
                return str(response)
            except Exception as e:
                return f"Fallo crítico en Proxy ({target}): {str(e)}"

    logger.info("Registro de Meta-Gateway (3 Herramientas Universales) completado.")
