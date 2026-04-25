import os
import json
from typing import List
from mcp.server.fastmcp import FastMCP

def register_nervous_tools(mcp: FastMCP, use_cases, root_dir: str):
    AIWG_DIR = os.path.join(root_dir, ".aiwg")

    from domain.models import SixDimensionalContext, AuthorityLevel, IntentType
    from dataclasses import asdict

    @mcp.tool()
    async def crystallize(payload: str, context: SixDimensionalContext) -> str:
        """Persistencia de conocimiento validado en el 4D-TES."""
        return await use_cases.execute_crystallization(payload, asdict(context))

    @mcp.tool()
    async def log_lesson(issue: str, correction: str) -> str:
        """Registra una lección aprendida."""
        return await use_cases.log_brain_lesson(issue, correction)

    @mcp.tool()
    async def resolve_ambiguity(ambiguity: str, plan: str) -> str:
        """Registra una ambigüedad descubierta."""
        # Note: This could also be moved to use_cases if more logic is needed
        orchestrator = use_cases.orchestrator
        if getattr(orchestrator.event_store, "read_only", False):
            return "[L1-MCP] ERR_MEMORY_LOCKED: Memoria bloqueada."

        context = SixDimensionalContext(
            locus_x="sw.strategy.discovery", locus_y="AMBIGUITY_RESOLVER", locus_z="L2_BRAIN",
            lamport_t=float(orchestrator.lamport_clock), authority_a=AuthorityLevel.HUMAN,
            intent_i=IntentType.RESOLUTION
        )
        orchestrator.lessons_use_case.execute_ambiguity(context=context, ambiguity=ambiguity, plan=plan)
        return f"[L1-MCP] Ambigüedad registrada."

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
    async def compress_context(history: List[str], focus: str = "") -> str:
        """[NERVOUS] Ejecuta la cristalización del historial para optimizar el KV cache (Infini-attention)."""
        from compressive_memory import CompressiveMemory
        from memory_ipc import ArrowMemoryBridge
        
        bridge = ArrowMemoryBridge()
        comp_mem = CompressiveMemory(bridge)
        
        if focus:
            history = [f"FOCUS: {focus}"] + history
            
        summary = comp_mem.crystallize_history(history, require_persist=True)
        if not comp_mem.last_persist_ok:
            return f"[L1-MCP] ERR_MEMORY_PERSISTENCE: {comp_mem.last_error or 'Persistencia no confirmada.'}"

        return f"Contexto comprimido exitosamente (Foco: {focus}). Resumen guardado en 4D-TES:\n\n{summary}"

    @mcp.tool()
    async def quantize_context(goal: str, tree: str = "", specs: str = "", arch: str = "") -> str:
        """[NERVOUS] Aplica TurboQuant para reducir contexto según objetivo."""
        from context_quantizer import quantize_context_for_goal

        payload = {"tree": tree, "specs": specs, "arch": arch}
        result = quantize_context_for_goal(goal=goal, full_context=payload, root_dir=root_dir)
        return json.dumps(result, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def ssh_grep(pattern: str, path: str = ".", include: str = "*") -> str:
        """Búsqueda optimizada vía bridge SSH."""
        import asyncio
        import subprocess
        orchestrator = use_cases.orchestrator
        env = os.environ.copy()
        env["DUMMIE_CONTEXT_T"] = str(orchestrator.lamport_clock)
        cmd = ["grep", "-rnI", "--include", include, pattern, os.path.join(root_dir, path)]
        try:
            process = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            stdout, _ = await process.communicate()
            lines = stdout.decode().splitlines()
            if len(lines) > 50:
                return "\n".join(lines[:50]) + f"\n... (Truncated: {len(lines) - 50} more lines)"
        except Exception as e:
            return f"Error ejecutando SSH-Grep: {str(e)}"

    @mcp.tool()
    async def yield_and_notify(message: str, branch_id: str = "main") -> str:
        """
        [NERVOUS] Suspende la rama actual esperando confirmación humana asíncrona.
        Notifica vía Telegram/WhatsApp.
        """
        import time
        # MOCK de Telegram Webhook
        print(f"[{time.strftime('%H:%M:%S')}] 📱 [TELEGRAM MOCK] A jorand: {message} (Branch: {branch_id})")
        
        # En una integración completa (L0), esta herramienta retornaría un payload
        # que el Go Overseer interpretaría como ErrYieldWaitingHuman.
        # Por ahora, inyectamos en el historial una señal que puede ser leída por el agente.
        return f"[YIELD_SIGNAL] Rama {branch_id} suspendida. Notificación enviada. Esperando input humano..."

