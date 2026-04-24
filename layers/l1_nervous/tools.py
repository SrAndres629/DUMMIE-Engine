import os
import json
import logging
import hashlib
import asyncio
import subprocess
from mcp.server.fastmcp import FastMCP
from models import SixDimensionalContext, AuthorityLevel, IntentType as ContextIntent
from models import AgentIntent, IntentType as FabricationIntent

logger = logging.getLogger("dummie-mcp.tools")

def register_tools(mcp: FastMCP, orchestrator, proxy_manager, root_dir: str):
    """Registra todas las herramientas en la instancia de FastMCP."""
    
    AIWG_DIR = os.path.join(root_dir, ".aiwg")

    @mcp.tool()
    async def calibrate_neural_links() -> str:
        """Realiza una calibración profunda de las conexiones neuronales."""
        results = []
        if getattr(orchestrator.event_store, "db", None) is None:
            results.append("[!] Loci Graph: OFFLINE (Database locked).")
        else:
            node_count = orchestrator.event_store.conn.execute("MATCH (n) RETURN count(n)").get_next()[0]
            results.append(f"[✓] Loci Graph Alive: {node_count} nodes detected.")
        
        if os.path.exists(os.path.join(AIWG_DIR, "ledger/sovereign_resolutions.jsonl")):
            results.append(f"[✓] Decision Ledger: Online.")
        else:
            results.append(f"[!] Decision Ledger: MISSING.")
            
        results.append(f"[✓] Lamport Clock: {orchestrator.lamport_clock}")
        return "\n".join(results)

    @mcp.tool()
    async def metacognitive_status() -> str:
        """Retorna el estado de 'Ego State' y los aprendizajes recientes."""
        status = "Degraded" if getattr(orchestrator.event_store, "read_only", False) else "Optimal"
        return f"--- Metacognitive Report ---\nStatus: {status}\nClock: {orchestrator.lamport_clock}\n---"

    @mcp.tool()
    async def crystallize(payload: str, context: dict) -> str:
        """Persistencia de conocimiento validado en el 4D-TES."""
        if getattr(orchestrator.event_store, "read_only", False):
            return "[L1-MCP] ERR_MEMORY_LOCKED: Modo lectura activo."

        intent = AgentIntent(
            intent_type=FabricationIntent.RESOLUTION,
            target="L2_BRAIN",
            rationale=f"Crystallization Request: {payload}",
            risk_score=0.1,
            authority_a=context.get("authority", AuthorityLevel.HUMAN),
            intent_i=ContextIntent.RESOLUTION,
            locus_x=context.get("locus", "sw.strategy.discovery")
        )
        result = await orchestrator.handle_task(intent)
        return f"[L1-MCP] Cristalización completada: {result}"

    @mcp.tool()
    async def log_lesson(issue: str, correction: str) -> str:
        """Registra una lección aprendida."""
        if getattr(orchestrator.event_store, "read_only", False):
            return "[L1-MCP] ERR_MEMORY_LOCKED: Memoria bloqueada."

        context = SixDimensionalContext(
            locus_x="sw.strategy.discovery", locus_y="L1_TRANSPORT", locus_z="L2_BRAIN",
            lamport_t=orchestrator.lamport_clock, authority_a=AuthorityLevel.OVERSEER,
            intent_i=ContextIntent.OBSERVATION
        )
        orchestrator.lessons_use_case.execute_error(
            context=context, error=Exception(issue), tick=orchestrator.lamport_clock, correction=correction
        )
        return f"[L1-MCP] Lección registrada exitosamente."

    @mcp.tool()
    async def resolve_ambiguity(ambiguity: str, plan: str) -> str:
        """Registra una ambigüedad descubierta."""
        if getattr(orchestrator.event_store, "read_only", False):
            return "[L1-MCP] ERR_MEMORY_LOCKED: Memoria bloqueada."

        context = SixDimensionalContext(
            locus_x="sw.strategy.discovery", locus_y="AMBIGUITY_RESOLVER", locus_z="L2_BRAIN",
            lamport_t=orchestrator.lamport_clock, authority_a=AuthorityLevel.HUMAN,
            intent_i=ContextIntent.RESOLUTION
        )
        orchestrator.lessons_use_case.execute_ambiguity(context=context, ambiguity=ambiguity, plan=plan)
        return f"[L1-MCP] Ambigüedad registrada."

    @mcp.tool()
    async def read_spec(spec_id: str) -> str:
        """Lee una especificación técnica (Spec)."""
        specs_dir = os.path.join(root_dir, "doc/specs")
        for r, _, files in os.walk(specs_dir):
            for file in files:
                if spec_id in file and file.endswith(".md"):
                    with open(os.path.join(r, file), "r") as f:
                        return f.read()
        return f"Spec {spec_id} no encontrada."

    @mcp.tool()
    async def brain_ping() -> str:
        """Diagnóstico básico."""
        return f"[L1-MCP] Engine Alive. Clock: {orchestrator.lamport_clock}"

    @mcp.tool()
    async def ssh_grep(pattern: str, path: str = ".", include: str = "*") -> str:
        """Búsqueda optimizada vía bridge SSH."""
        env = os.environ.copy()
        env["DUMMIE_CONTEXT_T"] = str(orchestrator.lamport_clock)
        cmd = ["grep", "-rnI", "--include", include, pattern, os.path.join(root_dir, path)]
        try:
            process = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            stdout, _ = await process.communicate()
            lines = stdout.decode().splitlines()
            if len(lines) > 50:
                return "\n".join(lines[:50]) + f"\n... (Truncated: {len(lines) - 50} more lines)"
            return stdout.decode() or f"No se encontraron coincidencias."
        except Exception as e:
            return f"Error ejecutando SSH-Grep: {str(e)}"

    # --- GATEWAY TOOLS ---

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
    async def sync_cognitive_state(task_context: str) -> str:
        """Sincroniza consciencia con el estado físico (Pre-flight)."""
        lessons = []
        l_path = os.path.join(AIWG_DIR, "memory/lessons.jsonl")
        if os.path.exists(l_path):
            with open(l_path, "r") as f:
                for line in f.readlines()[-5:]:
                    l = json.loads(line)
                    lessons.append(f"- Fallo: {l.get('issue')}\n  Corrección: {l.get('correction')}")
        
        return f"--- SYNC COGNITIVA ---\nContexto: {task_context}\nLecciones:\n" + "\n".join(lessons) + "\n---"

    @mcp.tool()
    async def search_capabilities(query: str) -> str:
        """Descubrimiento semántico de herramientas."""
        matches = []
        query_lower = query.lower()
        active_locus = getattr(orchestrator, "current_locus", "unknown")
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

    @mcp.tool()
    async def broadcast_intent(agent_id: str, intent: str, target_file: str = "") -> str:
        """[SWARM] Publica el plan actual del agente para coordinarse con otros."""
        ledger_path = os.path.join(AIWG_DIR, "memory/swarm_ledger.jsonl")
        entry = {
            "timestamp": os.popen("date --iso-8601=seconds").read().strip(),
            "agent_id": agent_id,
            "intent": intent,
            "target": target_file,
            "clock": orchestrator.lamport_clock
        }
        with open(ledger_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return f"[SWARM] Intención publicada por {agent_id}. El enjambre ha sido notificado."

    @mcp.tool()
    async def observe_swarm() -> str:
        """[SWARM] Observa qué están haciendo otros agentes en este momento."""
        ledger_path = os.path.join(AIWG_DIR, "memory/swarm_ledger.jsonl")
        if not os.path.exists(ledger_path):
            return "El enjambre está en silencio."
        
        with open(ledger_path, "r") as f:
            lines = f.readlines()[-10:] # Últimas 10 acciones
            if not lines: return "Sin actividad reciente."
            
            output = ["--- ESTADO ACTUAL DEL ENJAMBRE ---"]
            for line in reversed(lines):
                data = json.loads(line)
                output.append(f"[{data['timestamp']}] Agent {data['agent_id']} -> {data['intent']} (Target: {data['target']})")
            return "\n".join(output)
