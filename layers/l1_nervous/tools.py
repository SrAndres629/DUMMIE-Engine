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
from tools_impl.local_reasoning import register_local_reasoning_tools
from tools_impl.self_worktree import register_self_worktree_tools

logger = logging.getLogger("dummie-mcp.tools")

def register_tools(mcp: FastMCP, get_orchestrator, get_proxy, root_dir: str):
    """Dispatcher para el registro de herramientas (Arquitectura Hexagonal)."""
    
    logger.info("Iniciando registro de herramientas Meta-Gateway (L1-Hexagonal)...")
    
    # 1. Instancia interna para encapsular TODAS las herramientas nativas
    internal_mcp = FastMCP("Internal-Registry")

    # Registro diferido/perezoso para los dominios
    def setup_internal():
        orchestrator = get_orchestrator()
        proxy_manager = get_proxy()
        use_cases = BrainToolUseCases(orchestrator, proxy_manager)
        
        # Evitar doble registro si se llama varias veces
        if not internal_mcp._tool_manager.list_tools():
            register_core_tools(internal_mcp, use_cases, root_dir)
            register_swarm_tools(internal_mcp, use_cases, root_dir)
            register_nervous_tools(internal_mcp, use_cases, root_dir)
            register_knowledge_tools(internal_mcp, use_cases)
            register_sdd_tools(internal_mcp, use_cases)
            register_local_reasoning_tools(internal_mcp, use_cases, internal_mcp)
            register_self_worktree_tools(internal_mcp, root_dir)
        return orchestrator, proxy_manager
    
    # NOTA: Desactivamos register_gateway_tools porque el Meta-Gateway absorbe su funcionalidad.

    # 2. Exponer las 3 herramientas maestras (Meta-Gateway) en el MCP público
    
    @mcp.tool()
    async def dummie_discover_capabilities(query: str = "") -> str:
        """
        Descubre las capacidades disponibles en el sistema (locales y remotas).
        Si no sabes qué herramientas tienes, ejecuta esta primero.
        Utiliza búsqueda semántica si se proporciona un query.
        """
        _, proxy_manager = setup_internal()
        
        try:
            from layers.l2_brain.embedding_provider import EmbeddingProvider
        except ImportError:
            # Fallback si no está en el path absoluto
            import sys
            import os
            sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "layers", "l2_brain")))
            from embedding_provider import EmbeddingProvider

        query_vec = None
        if query and query != "*":
            logger.info(f"Generando vector semántico para búsqueda: '{query}'")
            query_vec = EmbeddingProvider.generate_vector(query)

        scored_tools = []
        
        # 1. Herramientas Locales
        local_tools = internal_mcp._tool_manager.list_tools()
        for t in local_tools:
            score = 0.0
            if query_vec:
                # Generar vector de la herramienta (Podríamos cachear esto)
                t_vec = EmbeddingProvider.generate_vector(f"{t.name} {t.description}")
                score = EmbeddingProvider.similarity(query_vec, t_vec)
            
            if not query or query == "*" or query.lower() in t.name.lower() or score > 0.4:
                scored_tools.append({
                    "id": f"local.{t.name}",
                    "desc": t.description,
                    "score": score,
                    "type": "LOCAL"
                })
        
        # 2. Herramientas Remotas
        try:
            for s_name, s_cfg in proxy_manager.servers.items():
                if s_cfg.get("disabled", False):
                    continue

                if not query:
                    profile = s_cfg.get("profile", "default")
                    capability_class = s_cfg.get("capability_class", "remote_capability")
                    rationale = s_cfg.get("rationale", "Remote MCP capability available through the gateway.")
                    scored_tools.append({
                        "id": f"remote.{s_name}",
                        "desc": f"[{profile}/{capability_class}] {rationale}",
                        "score": 0.0,
                        "type": "REMOTE_REGISTRY"
                    })
                    continue

                if query != "*":
                    haystack = " ".join([
                        s_name,
                        str(s_cfg.get("profile", "")),
                        str(s_cfg.get("capability_class", "")),
                        str(s_cfg.get("rationale", "")),
                    ]).lower()
                    if query.lower() not in haystack:
                        continue

                try:
                    r_tools = await proxy_manager.get_tools_for_server(s_name)
                    for t in r_tools:
                        name = t.get('name', 'unknown')
                        desc = t.get('description', 'No description')
                        score = 0.0
                        if query_vec:
                            t_vec = EmbeddingProvider.generate_vector(f"{name} {desc}")
                            score = EmbeddingProvider.similarity(query_vec, t_vec)
                        
                        if not query or query == "*" or query.lower() in name.lower() or score > 0.4:
                            scored_tools.append({
                                "id": f"{s_name}.{name}",
                                "desc": desc,
                                "score": score,
                                "type": "REMOTE"
                            })
                except Exception as e:
                    logger.warning(f"Error inspeccionando {s_name}: {e}")
        except Exception as e:
            logger.error(f"Error en proxy_manager: {e}")

        # Ordenar por score
        scored_tools.sort(key=lambda x: x["score"], reverse=True)

        output = ["=== CAPACIDADES DISPONIBLES (Ordenadas por Relevancia Semántica) ==="]
        for t in scored_tools:
            match_str = f" [Score: {t['score']:.2f}]" if query_vec else ""
            output.append(f"- {t['id']}: {t['desc']}{match_str}")
            
        if not scored_tools:
            output.append("No se encontraron capacidades que coincidan con la búsqueda.")
            
        return "\n".join(output)

    @mcp.tool()
    async def dummie_analyze_capability(target: str) -> str:
        """
        Analiza una capacidad específica para obtener sus argumentos y JSON Schema.
        Ejemplo target: 'local.crystallize' o 'git.git_status'
        """
        _, proxy_manager = setup_internal()
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
        orchestrator, proxy_manager = setup_internal()
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
