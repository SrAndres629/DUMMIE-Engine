import json
import logging
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from layers.l1_nervous.application.use_cases import BrainToolUseCases
from layers.l1_nervous.tools_impl.core import register_core_tools
from layers.l1_nervous.tools_impl.swarm import register_swarm_tools
from layers.l1_nervous.tools_impl.nervous import register_nervous_tools
from layers.l1_nervous.tools_impl.knowledge import register_knowledge_tools
from layers.l1_nervous.tools_impl.sdd import register_sdd_tools
from layers.l1_nervous.tools_impl.local_reasoning import register_local_reasoning_tools
from layers.l1_nervous.tools_impl.self_worktree import register_self_worktree_tools
from layers.l1_nervous.tools_impl.metacognition import register_metacognitive_tools
from layers.l1_nervous.capability_index import CapabilityIndex
from layers.l1_nervous.intelligent_intent_router import IntentRouter
from layers.l1_nervous.metacognitive_reasoner import MetacognitiveReasoner
from layers.l1_nervous.intelligence_evaluator import IntelligenceEvaluator
from layers.l1_nervous.smart_research_engine import SmartResearchEngine
from layers.l1_nervous.integration_planner import IntegrationPlanner

logger = logging.getLogger("dummie-mcp.tools")


def register_tools(mcp: FastMCP, get_orchestrator, get_proxy, root_dir: str):
    """Dispatcher para el registro de herramientas (Arquitectura Hexagonal)."""

    logger.debug("Iniciando registro de herramientas Meta-Gateway (L1-Hexagonal)...")

    # 1. Instancia interna para encapsular TODAS las herramientas nativas
    internal_mcp = FastMCP("Internal-Registry")

    # Registro diferido/perezoso para los dominios
    def setup_internal():
        orchestrator = get_orchestrator()
        proxy_manager = get_proxy()
        use_cases = BrainToolUseCases(orchestrator, proxy_manager)

        # [WAVE 8] Vincular Meta-Gateway al Orquestador
        if hasattr(orchestrator, "set_mcp_gateway"):
            orchestrator.set_mcp_gateway(proxy_manager)
        if not internal_mcp._tool_manager.list_tools():
            register_core_tools(internal_mcp, use_cases, root_dir)
            register_swarm_tools(internal_mcp, use_cases, root_dir)
            register_nervous_tools(internal_mcp, use_cases, root_dir)
            register_knowledge_tools(internal_mcp, use_cases)
            register_sdd_tools(internal_mcp, use_cases)
            register_local_reasoning_tools(internal_mcp, use_cases, internal_mcp)
            register_self_worktree_tools(internal_mcp, root_dir)
            register_metacognitive_tools(internal_mcp, orchestrator)
        return orchestrator, proxy_manager

    # NOTA: Desactivamos register_gateway_tools porque el Meta-Gateway absorbe su funcionalidad.

    # 2. Exponer las 3 herramientas maestras (Meta-Gateway) en el MCP público

    @mcp.tool()
    async def dummie_discover_capabilities(query: str = "") -> str:
        """
        Descubre las capacidades disponibles en el sistema (locales y remotas).
        Inteligencia ontológica exacta: entiende la intención y busca match exacto.
        Si no hay match: reporta 'herramienta necesaria no encontrada' y propone investigación.
        Skills se indexan pero NO se cargan hasta que se invocan (lazy loading).
        """
        _, proxy_manager = setup_internal()

        if hasattr(proxy_manager, "_load_config"):
            proxy_manager._load_config()

        index = CapabilityIndex()

        local_tools = internal_mcp._tool_manager.list_tools()
        for t in local_tools:
            index._capabilities.setdefault("local_tools", []).append(
                {
                    "id": f"local.{t.name}",
                    "name": t.name,
                    "type": "local",
                    "description": t.description,
                }
            )

        for s_name, s_cfg in proxy_manager.registry.servers.items():
            if s_cfg.get("disabled", False):
                continue
            profile = s_cfg.get("profile", "default")
            cc = s_cfg.get("capability_class", "remote")
            rationale = s_cfg.get("rationale", "")
            index.add_mcp_server_config(s_name, profile, cc, rationale)
            try:
                r_tools = await proxy_manager.registry.get_tools(s_name)
                index.add_mcp_tools(s_name, r_tools)
            except Exception:
                pass

        if not query or query == "*":
            all_items = []
            for cat, tools in index.list_all().items():
                for t in tools:
                    all_items.append(t)
            skills_info = index.list_skills()
            output = ["=== CAPACIDADES DISPONIBLES ==="]
            output.append(f"Total: {len(all_items)} tools + {len(skills_info)} skills")
            output.append("")

            output.append("--- MCP Tools ---")
            for t in sorted(all_items, key=lambda x: x["id"]):
                output.append(f"  {t['id']}: {t.get('description', '')[:120]}")

            output.append("")
            output.append("--- Skills Indexadas (carga lazy via gateway) ---")
            for s in sorted(skills_info, key=lambda x: x["id"]):
                cats = ", ".join(s.get("capabilities", []))
                output.append(f"  {s['id']}: {s.get('description', '')[:100]} [{cats}]")

            output.append("")
            output.append(
                "Para búsqueda inteligente: dummie_discover_capabilities(query='tu intencion')"
            )
            return "\n".join(output)

        reasoner = MetacognitiveReasoner()
        result = reasoner.analyze(query, index)

        output = [f"=== ANÁLISIS DE INTENCIÓN (MCIR) ==="]
        output.append(f"Query: '{query}'")
        if result.intent:
            output.append(
                f"Intención detectada: dominio={result.intent.domain}, "
                f"acción={result.intent.action}, "
                f"confianza={result.intent.confidence:.2f}"
            )

        output.append(f"Etapa: {result.stage}")
        output.append(f"Latencia: {result.latency_ms:.0f}ms")

        if result.found:
            match = result.match
            output.append(f"")
            output.append(f"✅ MATCH ENCONTRADO ({result.stage})")
            output.append(f"  Tool: {match.get('id', match.get('name', '?'))}")
            output.append(f"  Descripción: {match.get('description', '')[:200]}")

            if result.llm_decision and result.llm_decision.reasoning:
                output.append(
                    f"  Razonamiento LLM: {result.llm_decision.reasoning[:300]}"
                )
        else:
            output.append(f"")
            output.append(f"❌ HERRAMIENTA NECESARIA NO ENCONTRADA")
            output.append(f"  {result.message[:300]}")

            if result.metacognitive_questions:
                output.append(f"")
                output.append(f"  🤔 PREGUNTAS METACOGNITIVAS:")
                for q in result.metacognitive_questions:
                    output.append(f"    • {q}")

            if result.llm_decision and result.llm_decision.adaptation:
                output.append(f"")
                output.append(f"  🔧 SUGERENCIA DE ADAPTACIÓN:")
                output.append(f"    {result.llm_decision.adaptation[:300]}")

            if result.research_results:
                output.append(f"")
                output.append(f"  🔍 INVESTIGACIÓN EN GITHUB:")
                for r in result.research_results.get("results", [])[:5]:
                    output.append(
                        f"    • {r.get('name', '?')} "
                        f"({r.get('stars', 0)}★, {r.get('language', '?')})"
                    )
                    if r.get("url"):
                        output.append(f"      {r['url']}")

                planner = IntegrationPlanner()
                plan = planner.generate_plan(result.research_results)
                if plan:
                    output.append(f"")
                    output.append(f"  📋 PLAN DE INTEGRACIÓN:")
                    output.append(f"    Repo: {plan.name}")
                    output.append(f"    Riesgo: {plan.risk}")
                    for step in plan.steps[:4]:
                        output.append(f"    {step}")

        output.append("")
        output.append(f"--- Resumen del Índice ---")
        si = index.sum_index()
        output.append(
            f"{si['total_capabilities']} capacidades, {si['total_skills']} skills, "
            f"{si['categories']} categorías"
        )

        return "\n".join(output)

    @mcp.tool()
    async def dummie_report_config_path() -> str:
        """Reporta la ruta del archivo de configuración MCP que el gateway está usando."""
        _, proxy_manager = setup_internal()
        return f"CONFIG_PATH: {proxy_manager.config_path}"

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
                    return (
                        f"SCHEMA PARA '{target}':\n{json.dumps(t.parameters, indent=2)}"
                    )
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
                        return (
                            f"SCHEMA PARA '{target}':\n{json.dumps(schema, indent=2)}"
                        )
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
        logger.debug(f"META-GATEWAY EXECUTION: {target}")

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

                causal_id = hashlib.sha256(
                    f"{server_name}.{tool_name}.{orchestrator.lamport_clock}".encode()
                ).hexdigest()[:12]
                logger.debug(
                    f"Meta-Gateway Proxy [CausalID:{causal_id}]: {server_name}.{tool_name}"
                )

                admission = evaluate_remote_tool_admission(
                    server_name, tool_name, arguments
                )
                if admission.status != "ALLOW":
                    return f"SDD_BLOCKED: {admission.reason}"

                response = await proxy_manager.call_tool(
                    server_name, tool_name, arguments
                )

                if isinstance(response, dict) and "error" in response:
                    err = response["error"]
                    if "data" in err and "suggestion" in err["data"]:
                        return f"ERROR: {err.get('message', '')}\nSugerencia: {err['data']['suggestion']}"
                    return f"Error: {json.dumps(err)}"

                result = (
                    response.get("result", {})
                    if isinstance(response, dict)
                    else response
                )
                if isinstance(result, dict) and "content" in result:
                    content = result.get("content", [])
                    output = [
                        item["text"] for item in content if item.get("type") == "text"
                    ]
                    return "\n".join(output) if output else "Ejecución completada."

                return str(response)
            except Exception as e:
                return f"Fallo crítico en Proxy ({target}): {str(e)}"

    @mcp.tool()
    async def dummie_install_mcp(
        server_name: str,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        [WAVE 9] Instala un nuevo servidor MCP dinámicamente en el Gateway.
        """
        orchestrator, _ = setup_internal()
        if not hasattr(orchestrator, "auto_evolver"):
            return "Error: AutoEvolver no disponible en este contexto."

        success = await orchestrator.auto_evolver.autonomous_mcp_ingestion(
            server_name, command, args, env
        )
        if success:
            return f"Servidor MCP '{server_name}' instalado. Reinicia el Gateway para activar."
        return f"Fallo al instalar el servidor MCP '{server_name}'."

    @mcp.tool()
    async def dummie_self_program(mission: str) -> str:
        """
        [WAVE 9] DUMMIE escribe su propio código para resolver una misión técnica compleja.
        Detecta automáticamente dónde guardar el código basándose en su arquitectura de capas.
        """
        orchestrator, _ = setup_internal()
        if not hasattr(orchestrator, "auto_evolver") or not orchestrator.daemon:
            return "Error: AutoEvolver o Daemon no disponibles."

        result = await orchestrator.auto_evolver.self_program(
            mission, orchestrator.daemon
        )
        if result.get("success"):
            return f"MISIÓN CUMPLIDA: Código generado e instalado en {result['file_path']}.\nPreview:\n{result['code_preview']}"
        return f"MISIÓN FALLIDA: {result.get('error')}"

    @mcp.tool()
    async def metagateway_discover(query: str = "") -> str:
        """
        MetaGateway: descubre capacidades en los 5 gateways especializados (media, code, infra, knowledge, shell).
        Si se pasa query, devuelve el gateway destino para esa query.
        """
        from meta_router import MetaRouter

        router = MetaRouter()
        if query:
            result = router.route(query)
            return json.dumps(result, indent=2, ensure_ascii=False)
        caps = router.list_all_capabilities()
        return json.dumps(caps, indent=2, ensure_ascii=False)

    logger.debug("Registro de Meta-Gateway (5 Herramientas Universales) completado.")
