import json
import logging
import os
import re
import asyncio
from datetime import datetime, timezone
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
from layers.l1_nervous.discovery_indexing import CapabilityIndexCache

logger = logging.getLogger("dummie-mcp.tools")
_CAPABILITY_INDEX_CACHE = CapabilityIndexCache()

_CONJUNCTION_SPLITTERS = [
    re.compile(r"\band\b(?:\s+then\b)?", re.IGNORECASE),
    re.compile(r"\bademás\b", re.IGNORECASE),
    re.compile(r"\btambién\b", re.IGNORECASE),
    re.compile(r";\s*"),
    re.compile(r"\.\s+(?!\d)"),
]


def _split_compound(intent: str) -> list[str]:
    for pattern in _CONJUNCTION_SPLITTERS:
        parts = pattern.split(intent)
        if len(parts) > 1:
            return [p.strip() for p in parts if p.strip()]
    return [intent]


def _collect_6d_context() -> dict:
    from datetime import datetime, timezone
    from pathlib import Path
    import json as _j
    import os as _os

    root = Path(_os.environ.get("DUMMIE_ROOT", "/opt/dummie-engine"))
    aiwg = root / ".aiwg"
    now = datetime.now(timezone.utc).isoformat()

    ctx = {}

    try:
        ctx["temporal"] = {
            "timestamp_utc": now,
        }
    except Exception:
        ctx["temporal"] = {}

    try:
        ctx["spatial"] = {
            "dummie_root": str(root),
            "cwd": str(Path.cwd()),
        }
    except Exception:
        ctx["spatial"] = {}

    try:
        import subprocess

        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=5
        )
        models = [
            l.strip().split()[0]
            for l in result.stdout.strip().split("\n")[1:]
            if l.strip()
        ]
        ctx["semantic"] = {"available_models": models}
    except Exception:
        ctx["semantic"] = {"available_models": []}

    try:
        gateways_runtime = aiwg / "runtime" / "gateways"
        if gateways_runtime.exists():
            ready = [p.stem for p in gateways_runtime.glob("*.ready")]
        else:
            ready = []
        ctx["relational"] = {"gateways_ready": ready}
    except Exception:
        ctx["relational"] = {}

    try:
        lessons_path = aiwg / "memory" / "lessons.jsonl"
        if lessons_path.exists():
            lines = lessons_path.read_text().splitlines()
            recent = []
            for line in lines[-5:]:
                try:
                    recent.append(_j.loads(line))
                except Exception:
                    pass
            ctx["episodic"] = {"lesson_count": len(lines), "recent_lessons": recent}
        else:
            ctx["episodic"] = {"lesson_count": 0, "recent_lessons": []}
    except Exception:
        ctx["episodic"] = {}

    try:
        sessions = aiwg / "memory" / "session_ledger.jsonl"
        ledger_count = 0
        if sessions.exists():
            ledger_count = len(sessions.read_text().splitlines())
        ctx["instrumental"] = {"session_ledger_entries": ledger_count}
    except Exception:
        ctx["instrumental"] = {}

    return ctx


async def _verify_spec(spec_id: str) -> str:
    """Verify all claims in a spec by running their verify_cmd commands."""
    import yaml, subprocess
    from pathlib import Path

    if not spec_id:
        return json.dumps({"error": "spec_id is required"})

    specs_dir = Path(os.environ.get("DUMMIE_ROOT", "/opt/dummie-engine")) / "doc"
    spec_file = None
    for f in specs_dir.rglob("*.md"):
        content = f.read_text(errors="ignore")
        if not content.startswith("---"):
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        try:
            fm = yaml.safe_load(parts[1])
            if fm and (fm.get("id") == spec_id or fm.get("spec_id") == spec_id):
                spec_file = f
                break
        except Exception:
            continue

    if not spec_file:
        return json.dumps({"error": f"Spec '{spec_id}' not found"})

    content = spec_file.read_text(errors="ignore")
    parts = content.split("---", 2)
    fm = yaml.safe_load(parts[1]) if len(parts) >= 3 else {}
    title = fm.get("title", "")
    claims_data = fm.get("claims", [])
    if not claims_data:
        return json.dumps(
            {"spec_id": spec_id, "title": title, "claims": [], "summary": {"total": 0}}
        )

    results = []
    for claim in claims_data:
        cid = claim.get("id", "unknown")
        cmd = claim.get("verify_cmd", "")
        if not cmd:
            results.append(
                {"id": cid, "status": "UNVERIFIED", "reason": "no verify_cmd"}
            )
            continue
        try:
            proc = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(specs_dir.parent),
            )
            if proc.returncode == 0:
                results.append({"id": cid, "status": "PASS"})
            else:
                results.append(
                    {"id": cid, "status": "FAIL", "stderr": proc.stderr[:200]}
                )
        except subprocess.TimeoutExpired:
            results.append({"id": cid, "status": "ERROR", "reason": "timeout"})
        except Exception as e:
            results.append({"id": cid, "status": "ERROR", "reason": str(e)[:200]})

    p = sum(1 for r in results if r["status"] == "PASS")
    f = sum(1 for r in results if r["status"] == "FAIL")
    e = sum(1 for r in results if r["status"] == "ERROR")
    return json.dumps(
        {
            "spec_id": spec_id,
            "title": title,
            "claims": results,
            "summary": {"total": len(results), "passing": p, "failing": f, "errors": e},
        },
        indent=2,
        ensure_ascii=False,
    )


async def _verify_all_specs() -> str:
    """Scan all specs and verify all claims. Returns aggregate report."""
    import yaml
    from pathlib import Path

    specs_dir = Path(os.environ.get("DUMMIE_ROOT", "/opt/dummie-engine")) / "doc"
    all_results = []
    total_claims = 0
    total_passing = 0
    total_failing = 0

    for f in specs_dir.rglob("*.md"):
        content = f.read_text(errors="ignore")
        if not content.startswith("---"):
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        try:
            fm = yaml.safe_load(parts[1])
        except Exception:
            continue
        if not fm or not fm.get("claims"):
            continue
        spec_id = fm.get("id") or fm.get("spec_id") or f.relative_to(specs_dir).stem
        result = await _verify_spec(spec_id)
        result_data = json.loads(result)
        all_results.append(result_data)
        s = result_data.get("summary", {})
        total_claims += s.get("total", 0)
        total_passing += s.get("passing", 0)
        total_failing += s.get("failing", 0) + s.get("errors", 0)

    return json.dumps(
        {
            "specs_scanned": len(all_results),
            "specs_with_claims": [r["spec_id"] for r in all_results if r.get("claims")],
            "total_claims": total_claims,
            "passing": total_passing,
            "failing": total_failing,
            "details": all_results,
        },
        indent=2,
        ensure_ascii=False,
    )


def _admin_index_status() -> str:
    """Return summary of SPEC_INDEX.yaml: total specs, by layer, by status."""
    import yaml
    from pathlib import Path

    index_path = (
        Path(os.environ.get("DUMMIE_ROOT", "/opt/dummie-engine"))
        / "doc"
        / "SPEC_INDEX.yaml"
    )
    if not index_path.exists():
        return json.dumps({"error": "SPEC_INDEX.yaml not found"})

    data = yaml.safe_load(index_path.read_text())
    specs = data.get("specs", [])
    by_layer = {}
    by_status = {}
    for s in specs:
        layer = s.get("layer", "unknown")
        status = s.get("status", "unknown")
        by_layer[layer] = by_layer.get(layer, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1
    return json.dumps(
        {
            "total_specs": len(specs),
            "by_layer": by_layer,
            "by_status": by_status,
            "specs_with_claims": sum(1 for s in specs if s.get("claims", 0) > 0),
            "specs_with_deps": sum(1 for s in specs if s.get("dependencies")),
        },
        indent=2,
        ensure_ascii=False,
    )


def _admin_search_specs(query: str, layer: str) -> str:
    """Search SPEC_INDEX.yaml by query (matches title or id) and optional layer filter."""
    import yaml
    from pathlib import Path

    index_path = (
        Path(os.environ.get("DUMMIE_ROOT", "/opt/dummie-engine"))
        / "doc"
        / "SPEC_INDEX.yaml"
    )
    if not index_path.exists():
        return json.dumps({"error": "SPEC_INDEX.yaml not found"})

    data = yaml.safe_load(index_path.read_text())
    specs = data.get("specs", [])
    results = []
    query_lower = query.lower() if query else ""
    layer_lower = layer.lower() if layer else ""
    for s in specs:
        if layer_lower and s.get("layer", "").lower() != layer_lower:
            continue
        if query_lower:
            title = (s.get("title") or "").lower()
            sid = (s.get("id") or "").lower()
            if query_lower not in title and query_lower not in sid:
                continue
        results.append(
            {
                "id": s.get("id"),
                "title": s.get("title"),
                "path": s.get("path"),
                "status": s.get("status"),
                "layer": s.get("layer"),
                "claims": s.get("claims", 0),
                "dependencies": s.get("dependencies"),
            }
        )
    return json.dumps(
        {
            "query": query,
            "layer": layer,
            "matches": len(results),
            "results": results[:20],
        },
        indent=2,
        ensure_ascii=False,
    )


def _parse_remote_target(target: str) -> tuple[str, str | None]:
    """Parse a remote target into (server_name, tool_name).

    Handles these formats:
    - 'remote.n8n'              → ('n8n', None)
    - 'remote.n8n_api'          → ('n8n_api', None)
    - 'n8n.list_workflows'      → ('n8n', 'list_workflows')
    - 'remote.n8n_api.list_wf'  → ('n8n_api', 'list_wf')  # defensivo

    NOT handled here (caught before call):
    - 'local.crystallize' → handled by local. prefix
    """
    effective = target
    if effective.startswith("remote."):
        effective = effective[len("remote.") :]
    if "." in effective:
        server, tool = effective.split(".", 1)
        return server, tool
    return effective, None


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

    canonical_mode = os.environ.get("DUMMIE_CANONICAL_MODE", "").lower() in (
        "1",
        "true",
        "yes",
    )

    if not canonical_mode:
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

            local_tools = internal_mcp._tool_manager.list_tools()
            index = await _CAPABILITY_INDEX_CACHE.get_index(local_tools, proxy_manager)

            if not query or query == "*":
                all_items = []
                for cat, tools in index.list_all().items():
                    for t in tools:
                        all_items.append(t)
                skills_info = index.list_skills()
                output = ["=== CAPACIDADES DISPONIBLES ==="]
                output.append(
                    f"Total: {len(all_items)} tools + {len(skills_info)} skills"
                )
                output.append("")

                output.append("--- MCP Tools ---")
                for t in sorted(all_items, key=lambda x: x["id"]):
                    output.append(f"  {t['id']}: {t.get('description', '')[:120]}")

                output.append("")
                output.append("--- Skills Indexadas (carga lazy via gateway) ---")
                for s in sorted(skills_info, key=lambda x: x["id"]):
                    cats = ", ".join(s.get("capabilities", []))
                    output.append(
                        f"  {s['id']}: {s.get('description', '')[:100]} [{cats}]"
                    )

                output.append("")
                output.append(
                    "Para búsqueda inteligente: dummie_discover_capabilities(query='tu intencion')"
                )
                return "\n".join(output)

            reasoner = MetacognitiveReasoner()
            result = await reasoner.analyze(query, index)

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

            # [SMART] Cache result (async, non-blocking)
            if result.found and result.match:
                try:
                    from semantic_cache import SemanticRouteCache

                    _cache = SemanticRouteCache()
                    import time

                    _entry = {
                        "query": query,
                        "found": True,
                        "stage": result.stage,
                        "match": {
                            "id": result.match.get("id", ""),
                            "name": result.match.get("name", ""),
                            "description": str(result.match.get("description", ""))[
                                :200
                            ],
                        },
                        "latency_ms": result.latency_ms,
                        "cached_at": time.time(),
                    }
                    if result.intent:
                        _entry["intent"] = {
                            "domain": result.intent.domain,
                            "action": result.intent.action,
                            "confidence": result.intent.confidence,
                        }
                    asyncio.create_task(_cache.set(query, _entry))
                except Exception:
                    pass

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
                        return f"SCHEMA PARA '{target}':\n{json.dumps(t.parameters, indent=2)}"
                return f"Error: Capacidad local '{name}' no encontrada."
            else:
                # Remote capability — handles 'remote.n8n', 'n8n.tool', 'remote.n8n.tool'
                server_name, tool_name = _parse_remote_target(target)
                if tool_name is None:
                    # Server-level query: return server info without triggering discovery
                    cfg = proxy_manager.registry.get_server_config(server_name)
                    if not cfg:
                        return f"Error: Servidor '{server_name}' no encontrado en la configuracion."
                    r_tools = proxy_manager.registry.get_tools(server_name)
                    tool_count = len(r_tools)
                    return (
                        f"SERVIDOR: {server_name}\n"
                        f"  Descripcion: {cfg.get('rationale', 'N/A')}\n"
                        f"  Herramientas: {tool_count} registradas\n"
                        f"  Para ver schema de una herramienta: {server_name}.<tool_name>"
                    )
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
        async def dummie_execute_capability(
            target: str, arguments: Dict[str, Any]
        ) -> str:
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
                # Remote capability — handles 'remote.n8n_api', 'n8n.tool', 'remote.n8n.tool'
                server_name, tool_name = _parse_remote_target(target)
                if tool_name is None:
                    return (
                        f"Error: Target remoto debe tener el formato 'server.tool_name'. "
                        f"Servidor '{server_name}' encontrado, pero no se especifico herramienta."
                    )
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
                            item["text"]
                            for item in content
                            if item.get("type") == "text"
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
                result = await router.route(query)
                return json.dumps(result, indent=2, ensure_ascii=False)
            caps = router.list_all_capabilities()
            return json.dumps(caps, indent=2, ensure_ascii=False)

        @mcp.tool()
        async def metagateway_cot_reason(query: str) -> str:
            """
            Chain of Thought reasoning con 6D context enrichment.
            Procesa una query con todas las estrategias (exact, embedding, cross-encoder, CoT, LLM)
            y devuelve el razonamiento paso a paso, gateway destino, confianza y latencia.
            Incluye contexto 6D real (temporal, espacial, semantico, relacional, episodico, instrumental).
            """
            from routing import RoutingPipeline
            from routing.strategies.exact_match import ExactMatchStrategy
            from routing.strategies.embedding_match import EmbeddingMatchStrategy
            from routing.strategies.cross_encoder_rerank import (
                CrossEncoderRerankStrategy,
            )
            from routing.strategies.cot_reasoning import CoTReasoningStrategy
            from routing.strategies.llm_reasoning import LLMReasoningStrategy
            from dummie_sdk.models.model_registry import ModelRegistry

            import time
            from datetime import datetime, timezone
            from pathlib import Path

            t0_total = time.time()

            registry = ModelRegistry()
            pipeline = RoutingPipeline(
                [
                    ExactMatchStrategy(),
                    EmbeddingMatchStrategy(registry=registry),
                    CrossEncoderRerankStrategy(registry=registry),
                    CoTReasoningStrategy(registry=registry),
                    LLMReasoningStrategy(registry=registry),
                ],
                threshold=0.5,
            )

            t0 = time.time()
            result = await pipeline.route(query)
            elapsed_ms = round((time.time() - t0) * 1000, 1)

            output = {
                "query": query,
                "match": result.match,
                "gateway": result.gateway,
                "domain": result.domain,
                "action": result.action,
                "confidence": round(result.confidence, 4),
                "strategy": result.strategy,
                "latency_ms": elapsed_ms,
            }
            if hasattr(result, "reasoning") and result.reasoning:
                output["reasoning"] = result.reasoning
            if hasattr(result, "needs_clarification") and result.needs_clarification:
                output["needs_clarification"] = True
                output["clarifying_question"] = getattr(
                    result, "clarifying_question", ""
                )

            try:
                context_6d = _collect_6d_context()
                output["context_6d"] = context_6d
            except Exception:
                pass

            output["total_latency_ms"] = round((time.time() - t0_total) * 1000, 1)
            return json.dumps(output, indent=2, ensure_ascii=False)

    # --- canonical tools (always exposed) ---

    @mcp.tool()
    async def dummie_admin(action: str, params: dict = None) -> str:
        """
        Administrator tool: configuration, installation, and self-programming.

        Args:
            action: One of "config_path", "install_mcp", "self_program"
            params: Additional parameters for the action
        """
        _, proxy_manager = setup_internal()
        orchestrator, _ = setup_internal()

        if action == "config_path":
            return f"CONFIG_PATH: {proxy_manager.config_path}"

        if action == "install_mcp":
            if not hasattr(orchestrator, "auto_evolver"):
                return "Error: AutoEvolver no disponible en este contexto."
            server_name = (params or {}).get("server_name", "")
            command = (params or {}).get("command", "")
            args = (params or {}).get("args", [])
            env_vars = (params or {}).get("env")
            success = await orchestrator.auto_evolver.autonomous_mcp_ingestion(
                server_name, command, args, env_vars
            )
            if success:
                return f"Servidor MCP '{server_name}' instalado."
            return f"Fallo al instalar '{server_name}'."

        if action == "self_program":
            if not hasattr(orchestrator, "auto_evolver") or not orchestrator.daemon:
                return "Error: AutoEvolver o Daemon no disponibles."
            mission = (params or {}).get("mission", "")
            result = await orchestrator.auto_evolver.self_program(
                mission, orchestrator.daemon
            )
            if result.get("success"):
                return f"MISION CUMPLIDA: {result['file_path']}. Preview: {result['code_preview'][:200]}"
            return f"MISION FALLIDA: {result.get('error')}"

        if action == "verify_spec":
            return await _verify_spec((params or {}).get("spec_id", ""))

        if action == "verify_all":
            return await _verify_all_specs()

        if action == "index_status":
            return _admin_index_status()

        if action == "search_specs":
            query = (params or {}).get("query", "")
            layer = (params or {}).get("layer", "")
            return _admin_search_specs(query, layer)

        return f"Error: accion desconocida '{action}'. Use: config_path, install_mcp, self_program, verify_spec, verify_all, index_status, search_specs"

    @mcp.tool()
    async def dummie_process(
        intent: str,
        mode: str = "auto",
        skill: str = None,
        plan: dict = None,
        correction: dict = None,
    ) -> str:
        """
        [CANONICAL] Process a request through the SMART MetaGateway pipeline.

        Cache-first routing with fallback to LLM reasoning. Supports direct tool
        execution when the route is found with high confidence.

        Collaborative modes: plan (show plan, don't execute), confirm (execute pre-approved plan),
        reject (agent disagrees, re-route suggested), list (show available skills).

        Cache correction: semantic cache learns from agent feedback. When mode=reject
        with correction data, or when skill= succeeds, cache is updated for future queries.

        Args:
            intent: Natural language description of the task to perform.
            mode: "discover" (route only), "execute" (route + run tool),
                  "auto" (discover and auto-execute if confidence is high),
                  "plan" (show what will be done, don't execute),
                  "confirm" (execute a previously-approved plan),
                  "reject" (agent disagrees with plan),
                  "list" (show available skills).
            skill: Optional — force invocation of a specific skill by skill_id.
                   Skips SmartRouter classification. Works with plan/confirm/auto modes.
                   When used with confirm, the cache learns intent→skill mapping.
            plan: Required when mode="confirm" — the pre-approved plan to execute.
            correction: Optional — when mode="reject", provide corrected routing data.
                        Cache learns this correction and returns it for future queries.

        Internally uses: SemanticRouteCache, SmartRouter, ContextBudgetRouter,
        MetacognitiveReasoner, MCPProxyManager, SkillExecutor.
        """
        import time as _time

        t_start = _time.monotonic()

        if not intent or not intent.strip():
            return json.dumps({"error": True, "message": "Intent cannot be empty"})

        valid_modes = (
            "discover",
            "execute",
            "auto",
            "plan",
            "confirm",
            "reject",
            "list",
            "parallel",
            "load",
        )
        if mode not in valid_modes:
            mode = "auto"

        # ── mode=load: load a spec from SPEC_INDEX.yaml by id or title ──
        if mode == "load":
            import yaml as _yaml
            from pathlib import Path as _Path

            root = _Path(os.environ.get("DUMMIE_ROOT", "/opt/dummie-engine"))
            index = root / "doc" / "SPEC_INDEX.yaml"
            if not index.exists():
                return json.dumps({"error": "SPEC_INDEX.yaml not found"})
            data = _yaml.safe_load(index.read_text())
            found = None
            intent_lower = intent.strip().lower()
            for s in data.get("specs", []):
                sid = (s.get("id") or "").lower()
                title = (s.get("title") or "").lower()
                if intent_lower == sid or intent_lower in sid or intent_lower in title:
                    found = s
                    break
            if not found:
                return json.dumps(
                    {
                        "error": f"Spec not found: '{intent}'. Use search_specs to find specs."
                    }
                )
            sp = root / found["path"]
            if not sp.exists():
                return json.dumps({"error": f"Spec file not found: {found['path']}"})
            content = sp.read_text(errors="ignore")
            return json.dumps(
                {
                    "mode": "load",
                    "spec_id": found.get("id"),
                    "title": found.get("title"),
                    "path": found.get("path"),
                    "status": found.get("status"),
                    "layer": found.get("layer"),
                    "claims": found.get("claims", 0),
                    "dependencies": found.get("dependencies"),
                    "content": content[:8000],
                    "truncated": len(content) > 8000,
                },
                indent=2,
                ensure_ascii=False,
            )

        # ── mode=list: return skill catalog ──
        if mode == "list":
            try:
                from skill_executor import SkillExecutor

                _se = SkillExecutor(None)
                skills = _se.list_all()
                return json.dumps(
                    {
                        "mode": "list",
                        "skills": skills,
                        "count": len(skills),
                        "hint": "Use skill=<skill_id> with any mode to force a specific skill. "
                        "Example: dummie_process(intent='...', mode='plan', skill='tdd')",
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            except Exception as e:
                return json.dumps(
                    {"error": True, "message": f"Failed to list skills: {e}"}
                )

        # ── mode=parallel: split compound intent and execute concurrently ──
        if mode == "parallel" or (mode == "auto" and len(_split_compound(intent)) > 1):
            _, proxy_mgr = setup_internal()
            sub_intents = _split_compound(intent)
            if len(sub_intents) == 1:
                mode = "auto"
            else:

                async def _process_one(sub: str):
                    try:
                        from semantic_cache import SemanticRouteCache

                        _sc = SemanticRouteCache()
                        cached = await _sc.get(sub)
                        if cached:
                            return {"intent": sub, "cached": True, "result": cached}
                    except Exception:
                        pass
                    try:
                        from smart_router import SmartRouter

                        _sr = SmartRouter()
                        route = await _sr.route(sub, {})
                        if route.get("match") and route.get("tools"):
                            t = route["tools"][0]
                            r = await proxy_mgr.call_tool(
                                t["server"], t["tool"], t.get("arguments", {})
                            )
                            return {
                                "intent": sub,
                                "routed": True,
                                "result": str(r)[:500],
                            }
                    except Exception as e:
                        return {"intent": sub, "error": str(e)}
                    return {"intent": sub, "result": "routing failed"}

                t_seq = _time.monotonic()
                sub_results = await asyncio.gather(
                    *[_process_one(si) for si in sub_intents], return_exceptions=True
                )
                resolved = []
                for si, r in zip(sub_intents, sub_results):
                    if isinstance(r, Exception):
                        resolved.append({"intent": si, "error": str(r)})
                    elif isinstance(r, dict):
                        resolved.append(r)
                    else:
                        resolved.append({"intent": si, "result": str(r)[:500]})
                sequential_est = sum(len(str(r)) / 10 for r in resolved)
                return json.dumps(
                    {
                        "mode": "parallel",
                        "intent": intent,
                        "sub_intents": sub_intents,
                        "sub_count": len(sub_intents),
                        "sub_results": resolved,
                        "total_latency_ms": (_time.monotonic() - t_start) * 1000,
                        "sequential_est_ms": sequential_est,
                        "speedup": f"{max(sequential_est / max((_time.monotonic() - t_start) * 1000, 1), 1):.1f}x",
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                return json.dumps(
                    {
                        "mode": "parallel",
                        "intent": intent,
                        "sub_intents": sub_intents,
                        "sub_count": len(sub_intents),
                        "sub_results": sub_results,
                        "total_latency_ms": (_time.monotonic() - t_start) * 1000,
                        "sequential_est_ms": sequential_est,
                        "speedup": f"{sequential_est / max((_time.monotonic() - t_start) * 1000, 1):.1f}x",
                    },
                    indent=2,
                    ensure_ascii=False,
                )

        # ── mode=reject: cache correction learning ──
        if mode == "reject":
            result = {
                "mode": "reject",
                "intent": intent,
                "action": "Plan rejected by agent. Re-route with mode=plan for fresh routing.",
                "total_latency_ms": (_time.monotonic() - t_start) * 1000,
            }

            # Spec 227: If agent provides a correction, cache learns it
            if correction and _cache:
                try:
                    await _cache.set(
                        intent,
                        {
                            "query": intent,
                            "match": True,
                            "domain": correction.get("domain"),
                            "confidence": 0.95,
                            "correction": correction,
                            "mode": correction.get("mode", "auto"),
                            "skill_name": correction.get("skill_name"),
                            "suggested_tool": correction.get("suggested_tool"),
                        },
                    )
                    result["cache_updated"] = True
                    result["action"] = (
                        "Correction cached. This correction will be used for future "
                        "similar queries."
                    )
                    logger.info(
                        "Cache correction learned for intent: %s → %s",
                        intent[:60],
                        correction.get("domain", "unknown"),
                    )
                except Exception as e:
                    logger.warning("Cache correction failed (benign): %s", e)

            return json.dumps(result, indent=2, ensure_ascii=False)

        # ── mode=confirm: execute pre-approved plan ──
        if mode == "confirm":
            if not plan or not plan.get("steps"):
                return json.dumps(
                    {
                        "error": True,
                        "message": "confirm mode requires a 'plan' with 'steps'",
                    }
                )
            result = await self._execute_plan(intent, plan, t_start)
            # Spec 227: cache successful confirm executions for future learning
            try:
                from semantic_cache import SemanticRouteCache

                _sc = SemanticRouteCache()
                asyncio.create_task(
                    _sc.set(
                        intent,
                        {
                            "query": intent,
                            "plan": plan,
                            "result_summary": str(result)[:500],
                        },
                    )
                )
            except Exception:
                pass
            return result

        # ── skill= param: force skill invocation ──
        if skill:
            try:
                from skill_executor import SkillExecutor
            except ImportError:
                return json.dumps(
                    {"error": True, "message": "SkillExecutor not available"}
                )
            _, proxy_mgr = setup_internal()
            _s_exec = SkillExecutor(proxy_mgr)
            _s_template = _s_exec.get(skill)
            if not _s_template:
                available = [s["skill_id"] for s in _s_exec.list_all()]
                return json.dumps(
                    {
                        "error": True,
                        "message": f"Skill '{skill}' not found. Available: {available}",
                    },
                    indent=2,
                    ensure_ascii=False,
                )

            _s_steps = [
                {
                    "id": s.step_id,
                    "description": s.description,
                    "server": s.server,
                    "tool": s.tool,
                    "depends_on": s.depends_on,
                    "arguments": s.arguments,
                }
                for s in _s_template.steps
            ]

            if mode == "plan":
                plan_built = {
                    "mode": "plan",
                    "intent": intent,
                    "skill": skill,
                    "skill_name": _s_template.name,
                    "skill_description": _s_template.description,
                    "deliberate_invocation": True,
                    "steps": _s_steps,
                    "estimated_tokens": len(_s_steps) * 400,
                    "total_latency_ms": (_time.monotonic() - t_start) * 1000,
                }
                # Spec 227: cache deliberate skill plan for future learning
                try:
                    from semantic_cache import SemanticRouteCache

                    _sc = SemanticRouteCache()
                    asyncio.create_task(_sc.set(intent, plan_built))
                except Exception:
                    pass
                return json.dumps(plan_built, indent=2, ensure_ascii=False)

            _s_result = await _s_exec.execute(_s_template, intent)
            response = {
                "mode": mode,
                "intent": intent,
                "skill": skill,
                "skill_name": _s_template.name,
                "deliberate_invocation": True,
                "steps": len(_s_steps),
                "skill_executed": True,
                "result": _s_result.get("outputs", _s_result)
                if isinstance(_s_result, dict)
                else str(_s_result),
                "total_latency_ms": (_time.monotonic() - t_start) * 1000,
            }
            # Spec 227: cache deliberate skill execution for future queries
            try:
                from semantic_cache import SemanticRouteCache

                _sc = SemanticRouteCache()
                asyncio.create_task(_sc.set(intent, response))
            except Exception:
                pass
            return json.dumps(response, indent=2, ensure_ascii=False)

        # ── 1. Cache check ──
        try:
            from semantic_cache import SemanticRouteCache

            _cache = SemanticRouteCache()
            cached = await _cache.get(intent)
            if cached:
                result = dict(cached)
                result["_route_from_cache"] = True
                result["total_latency_ms"] = (_time.monotonic() - t_start) * 1000
                return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug("SMART cache check failed: %s", e)

        # ── 2. Context budget ──
        try:
            from context_budget_tools import ContextBudgetRouter

            _budget = ContextBudgetRouter()
            tools_tier = _budget.get_tools_for_budget(8192)
            tier_level = _budget._resolve_tier(8192)
        except Exception:
            tools_tier = {}
            tier_level = 1

        # ── 3. Capability index ──
        _, proxy_mgr = setup_internal()
        if hasattr(proxy_mgr, "_load_config"):
            proxy_mgr._load_config()
        local_tools = internal_mcp._tool_manager.list_tools()
        index = await CapabilityIndexCache().get_index(local_tools, proxy_mgr)

        # ── 4. SmartRouter classification ──
        route_info = None
        smart_used = False
        try:
            from smart_router import SmartRouter

            _router = SmartRouter()
            tier_tools = tools_tier.get(tier_level, {}) if tools_tier else {}
            route = await _router.route(intent, tier_tools)
            if route.get("match") and route.get("confidence", 0) >= 0.8:
                route_info = route
                smart_used = True
        except Exception:
            logger.debug("SmartRouter failed, falling back to LLM", exc_info=True)

        # ── 4.5 Skill match ──
        matched_skill = None
        matched_skill_id = None
        skill_steps = None
        skill_result = None
        try:
            from skill_executor import SkillExecutor

            _executor = SkillExecutor(proxy_mgr)
            matched_skill = await _executor.match(intent)
            if matched_skill:
                matched_skill_id = matched_skill.skill_id
                skill_steps = [
                    {
                        "id": s.step_id,
                        "description": s.description,
                        "server": s.server,
                        "tool": s.tool,
                        "depends_on": s.depends_on,
                        "arguments": s.arguments,
                    }
                    for s in matched_skill.steps
                ]
                skill_result = await _executor.execute(matched_skill, intent)
        except Exception:
            logger.debug("Skill executor failed", exc_info=True)

        # ── 4.6 Plan mode: return plan without executing ──
        if mode == "plan":
            plan_built = {
                "mode": "plan",
                "intent": intent,
                "domain": route_info.get("domain") if route_info else None,
                "skill": matched_skill_id,
                "suggested_skill": matched_skill_id,
                "skill_name": matched_skill.name if matched_skill else None,
                "skill_description": matched_skill.description
                if matched_skill
                else None,
                "confidence": route_info.get("confidence", 0.0) if route_info else 0.0,
                "strategy": route_info.get("strategy", "unknown")
                if route_info
                else "unknown",
                "steps": skill_steps or [],
                "estimated_tokens": len(skill_steps or []) * 400,
                "total_latency_ms": (_time.monotonic() - t_start) * 1000,
            }
            try:
                if matched_skill_id:
                    from semantic_cache import SemanticRouteCache

                    _sc2 = SemanticRouteCache()
                    asyncio.create_task(_sc2.set(intent, plan_built))
            except Exception:
                pass
            return json.dumps(plan_built, indent=2, ensure_ascii=False)

        # ── 4.7 Auto mode, confidence >= 0.85 → execute silently ──
        if (
            mode == "auto"
            and route_info
            and route_info.get("confidence", 0) >= 0.85
            and skill_result
        ):
            response = {
                "mode": mode,
                "intent": intent,
                "collaboration": "auto",
                "skill": matched_skill_id,
                "steps": len(skill_steps or []),
                "skill_executed": True,
                "result": skill_result.get("result", skill_result)
                if isinstance(skill_result, dict)
                else str(skill_result),
                "total_latency_ms": (_time.monotonic() - t_start) * 1000,
            }
            try:
                from semantic_cache import SemanticRouteCache

                _sc2 = SemanticRouteCache()
                asyncio.create_task(_sc2.set(intent, response))
            except Exception:
                pass
            return json.dumps(response, indent=2, ensure_ascii=False)

        # ── 4.8 Auto mode, confidence < 0.85 → suggest plan ──
        if mode == "auto" and route_info and route_info.get("confidence", 0) < 0.85:
            return json.dumps(
                {
                    "mode": "plan",
                    "intent": intent,
                    "collaboration": "low_confidence",
                    "suggestion": (
                        "Low confidence routing detected. "
                        "Review plan and call again with mode=confirm to execute, "
                        "or mode=reject to re-route."
                    ),
                    "domain": route_info.get("domain"),
                    "skill": matched_skill_id,
                    "suggested_skill": matched_skill_id,
                    "skill_name": matched_skill.name if matched_skill else None,
                    "skill_description": matched_skill.description
                    if matched_skill
                    else None,
                    "confidence": route_info.get("confidence", 0.0),
                    "strategy": route_info.get("strategy", "unknown"),
                    "steps": skill_steps or [],
                    "total_latency_ms": (_time.monotonic() - t_start) * 1000,
                },
                indent=2,
                ensure_ascii=False,
            )

        # ── 5. [Fallback] MetacognitiveReasoner ──
        if not route_info:
            reasoner = MetacognitiveReasoner()
            result = await reasoner.analyze(intent, index)
            if result.found and result.match:
                match_id = result.match.get("id", "")
                server_name, tool_name = _parse_remote_target(match_id)
                route_info = {
                    "match": True,
                    "domain": result.intent.domain if result.intent else None,
                    "action": result.intent.action if result.intent else None,
                    "confidence": result.intent.confidence if result.intent else 0.0,
                    "servers": [server_name],
                    "tools": [
                        {
                            "server": server_name,
                            "tool": tool_name,
                            "arguments": {},
                        }
                        if tool_name
                        else {}
                    ],
                }
            else:
                route_info = {
                    "match": False,
                    "message": getattr(result, "message", str(result)),
                }

        # ── 6. Execute (if mode allows) ──
        execution = {"executed": False, "result": None, "error": None}
        if route_info.get("match") and mode in ("execute", "auto") and smart_used:
            tools = route_info.get("tools", [])
            if tools and tools[0]:
                t0_exec = _time.monotonic()
                try:
                    exec_result = await proxy_mgr.call_tool(
                        tools[0]["server"],
                        tools[0]["tool"],
                        tools[0].get("arguments", {}),
                    )
                    execution["executed"] = True
                    try:
                        from result_compression import compress

                        execution["result"] = compress(str(exec_result))
                    except ImportError:
                        execution["result"] = str(exec_result)[:1000]
                    execution["latency_ms"] = (_time.monotonic() - t0_exec) * 1000
                except Exception as e:
                    execution["error"] = str(e)

        # ── 7. Build response ──
        response = {
            "intent": intent,
            "mode": mode,
            "routing": route_info,
            "execution": execution,
            "total_latency_ms": (_time.monotonic() - t_start) * 1000,
        }

        # ── 8. Cache result ──
        try:
            if route_info.get("match"):
                from semantic_cache import SemanticRouteCache

                _cache2 = SemanticRouteCache()
                asyncio.create_task(_cache2.set(intent, response))
        except Exception:
            pass

        return json.dumps(response, indent=2, ensure_ascii=False)

    async def _execute_plan(self, intent: str, plan: dict, t_start: float) -> str:
        """Execute a pre-approved execution plan."""
        _, proxy_mgr = setup_internal()
        try:
            from result_compression import compress as _comp
        except ImportError:
            _comp = lambda s: s  # noop
        results = []
        for step in plan.get("steps", []):
            try:
                result = await proxy_mgr.call_tool(
                    step["server"], step["tool"], step.get("arguments", {})
                )
                results.append(
                    {
                        "step_id": step.get("id", "?"),
                        "server": step["server"],
                        "tool": step["tool"],
                        "result": _comp(str(result)),
                    }
                )
                results.append(
                    {
                        "step_id": step.get("id", "?"),
                        "server": step["server"],
                        "tool": step["tool"],
                        "result": (
                            compress(str(result))
                            if "compress" in dir()
                            else str(result)[:500]
                        ),
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "step_id": step.get("id", "?"),
                        "server": step["server"],
                        "tool": step["tool"],
                        "error": str(e),
                    }
                )
        response = {
            "mode": "confirm",
            "intent": intent,
            "collaboration": "agent_approved",
            "steps_executed": len(results),
            "errors": sum(1 for r in results if "error" in r),
            "results": results,
            "total_latency_ms": (_time.monotonic() - t_start) * 1000,
        }
        return json.dumps(response, indent=2, ensure_ascii=False)

    logger.debug("Registro de Meta-Gateway (5 Herramientas Universales) completado.")
