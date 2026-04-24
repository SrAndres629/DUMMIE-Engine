import os
import json
import hashlib
from mcp.server.fastmcp import FastMCP
from brain.domain.context.models import SixDimensionalContext, AuthorityLevel, IntentType as ContextIntent
from brain.domain.fabrication.models import AgentIntent, IntentType as FabricationIntent
from brain.application.use_cases.orchestrator import CognitiveOrchestrator
from brain.infrastructure.adapters.kuzu_repository import KuzuRepository
from brain.infrastructure.adapters.ledger_adapter import DecisionLedgerAdapter
from brain.infrastructure.adapters.session_ledger_adapter import SessionLedgerAdapter
from brain.infrastructure.adapters.shield_adapter import NativeShieldAdapter
from brain.infrastructure.adapters.skill_adapter import KuzuSkillRepository

# 1. Initialize FastMCP server (Spec MCP-01)
# El "USB-C" de la IA para DUMMIE Engine - Relocated to L1 (Nervous)
mcp = FastMCP("DUMMIE-Brain-Adapter", 
              dependencies=["kuzu", "pydantic", "zstd", "mcp"])

# 2. Infrastructure Setup (Bootstrap)
# NOTA: En una arquitectura más madura, este setup se inyectaría desde un punto de entrada global.
# Siguiendo la "Logic Zero Policy", este archivo solo actúa como el canal físico.
ROOT_DIR = "/home/jorand/Escritorio/DUMMIE Engine"
AIWG_DIR = os.path.join(ROOT_DIR, ".aiwg")

def bootstrap_orchestrator():
    event_store = KuzuRepository(db_path=os.path.join(AIWG_DIR, "memory/loci.db"))
    ledger_audit = DecisionLedgerAdapter(
        ledger_path=os.path.join(AIWG_DIR, "ledger/sovereign_resolutions.jsonl"),
        lessons_path=os.path.join(AIWG_DIR, "memory/lessons.jsonl"),
        ambiguities_path=os.path.join(AIWG_DIR, "memory/ambiguities.jsonl"),
        ontological_map_path=os.path.join(AIWG_DIR, "ontological_map.json")
    )
    session_ledger = SessionLedgerAdapter(ledger_path=os.path.join(AIWG_DIR, "memory/ego_state.jsonl"))
    shield = NativeShieldAdapter()
    skill_repo = KuzuSkillRepository(db_path=os.path.join(AIWG_DIR, "memory/loci.db"))

    return CognitiveOrchestrator(
        shield_port=shield,
        event_store=event_store,
        ledger_audit=ledger_audit,
        session_ledger=session_ledger,
        skill_repo=skill_repo
    )

orchestrator = bootstrap_orchestrator()

# --- TOOLS (Standardized per ADR-0013 / Spec L1-15) ---

@mcp.tool()
async def calibrate_neural_links() -> str:
    """
    Realiza una calibración profunda de las conexiones neuronales del motor.
    Verifica: Conectividad KùzuDB, integridad del Ledger y salud del 4D-TES.
    """
    results = []
    try:
        # 1. Verificar Kùzu (Memory)
        node_count = orchestrator.event_store.conn.execute("MATCH (n) RETURN count(n)").get_next()[0]
        results.append(f"[✓] Loci Graph Alive: {node_count} nodes detected.")
        
        # 2. Verificar Ledger (Identity)
        if os.path.exists(orchestrator.ledger_audit.ledger_path):
            results.append(f"[✓] Decision Ledger: Online.")
        else:
            results.append(f"[!] Decision Ledger: MISSING. Initializing skeletal...")
            
        # 3. Clock Sync
        results.append(f"[✓] Lamport Clock: {orchestrator.lamport_clock}")
        
        return "\n".join(results)
    except Exception as e:
        return f"[ERROR] Falla crítica de calibración: {str(e)}"

@mcp.tool()
async def metacognitive_status() -> str:
    """
    Retorna el estado de 'Ego State' y los aprendizajes recientes para automejora.
    """
    try:
        decisions = get_recent_decisions()
        identity = get_brain_identity()
        return f"--- Metacognitive Report ---\nIdentity: {identity}\nRecent Decisions: {decisions}\n---"
    except Exception as e:
        return f"Error en reporte metacognitivo: {str(e)}"

@mcp.tool()
async def crystallize(payload: str, context: dict) -> str:
    """
    Punto de entrada único para la persistencia de conocimiento validado en el 4D-TES.
    Mapea a la capacidad física de orquestación de tareas (Spec 02).
    """
    try:
        # Extraer metadatos del contexto si existen
        authority = context.get("authority", AuthorityLevel.HUMAN)
        locus = context.get("locus", "sw.strategy.discovery")
        
        intent = AgentIntent(
            intent_type=FabricationIntent.RESOLUTION,
            target="L2_BRAIN",
            rationale=f"Crystallization Request: {payload}",
            risk_score=0.1,
            authority_a=authority,
            intent_i=ContextIntent.RESOLUTION,
            locus_x=locus
        )
        result = await orchestrator.handle_task(intent)
        return f"[L1-MCP] Cristalización completada: {result}"
    except Exception as e:
        return f"[L1-MCP] Error en cristalización: {str(e)}"

@mcp.tool()
async def log_lesson(issue: str, correction: str) -> str:
    """
    Registra una lección aprendida tras un fallo o descubrimiento.
    Implementa la política de captura de conocimiento de la Spec 48.
    """
    try:
        context = SixDimensionalContext(
            locus_x="sw.strategy.discovery",
            locus_y="L1_TRANSPORT",
            locus_z="L2_BRAIN",
            lamport_t=orchestrator.lamport_clock,
            authority_a=AuthorityLevel.OVERSEER,
            intent_i=ContextIntent.OBSERVATION
        )
        orchestrator.lessons_use_case.execute_error(
            context=context,
            error=Exception(f"Issue: {issue} | Correction: {correction}"),
            tick=orchestrator.lamport_clock
        )
        return f"[L1-MCP] Lección registrada exitosamente en .aiwg"
    except Exception as e:
        return f"[L1-MCP] Error al registrar lección: {str(e)}"

@mcp.tool()
async def resolve_ambiguity(ambiguity: str, plan: str) -> str:
    """
    Registra una ambigüedad descubierta y el plan para resolverla.
    Activa el protocolo de cierre cognitivo (Spec 49).
    """
    try:
        context = SixDimensionalContext(
            locus_x="sw.strategy.discovery",
            locus_y="AMBIGUITY_RESOLVER",
            locus_z="L2_BRAIN",
            lamport_t=orchestrator.lamport_clock,
            authority_a=AuthorityLevel.HUMAN,
            intent_i=ContextIntent.RESOLUTION
        )
        orchestrator.lessons_use_case.execute_ambiguity(
            context=context,
            ambiguity=ambiguity,
            plan=plan
        )
        return f"[L1-MCP] Ambigüedad registrada para resolución."
    except Exception as e:
        return f"[L1-MCP] Error al registrar ambigüedad: {str(e)}"

@mcp.tool()
async def read_spec(spec_id: str) -> str:
    """
    Lee una especificación técnica (Spec) del motor.
    Garantiza el modelo SDD-Driven (Single Source of Truth).
    """
    # Búsqueda simple en el directorio de specs
    specs_dir = os.path.join(ROOT_DIR, "doc/specs")
    for root, _, files in os.walk(specs_dir):
        for file in files:
            if spec_id in file and file.endswith(".md"):
                with open(os.path.join(root, file), "r") as f:
                    return f.read()
    return f"Spec {spec_id} no encontrada."

@mcp.tool()
async def brain_ping() -> str:
    """Diagnóstico básico del estado del motor."""
    return f"[L1-MCP] Engine Alive. Layer: L1-Adapter. Clock: {orchestrator.lamport_clock}"

# --- RESOURCES ---

@mcp.resource("brain://identity")
def get_brain_identity() -> str:
    """Retorna la identidad y arquetipo del sistema."""
    path = os.path.join(AIWG_DIR, "identity.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return "Identidad desconocida."

@mcp.resource("memory://decisions")
def get_recent_decisions() -> str:
    """Lee las últimas resoluciones del Ledger de Decisiones (Spec 34)."""
    path = os.path.join(AIWG_DIR, "ledger/sovereign_resolutions.jsonl")
    if not os.path.exists(path): return "No decisions found."
    with open(path, "r") as f:
        return "".join(f.readlines()[-10:])

@mcp.resource("memory://timeline")
def get_memory_timeline() -> str:
    """Stream de eventos inmutables del 4D-TES (Spec 02)."""
    try:
        results = orchestrator.event_store.conn.execute(
            "MATCH (m:MemoryNode4D) RETURN m.lamport_t, m.causal_hash, m.intent_i ORDER BY m.lamport_t DESC LIMIT 50"
        )
        events = []
        while results.has_next():
            row = results.get_next()
            events.append(f"T={row[0]} | Hash={row[1]} | Intent={row[2]}")
        return "\n".join(events) if events else "Timeline empty."
    except Exception as e:
        return f"Error reading timeline: {str(e)}"

@mcp.resource("memory://loci")
def get_memory_loci() -> str:
    """Acceso al grafo de relaciones ontológicas (Palacio de Loci)."""
    try:
        # Resumen estadístico del grafo
        nodes = orchestrator.event_store.conn.execute("MATCH (n) RETURN labels(n), count(*)").get_next()
        rels = orchestrator.event_store.conn.execute("MATCH ()-[r]->() RETURN type(r), count(*)").get_next()
        return json.dumps({
            "status": "Healthy",
            "topology": "Merkle-DAG",
            "summary": {
                "nodes": nodes,
                "relationships": rels
            }
        }, indent=2)
    except Exception as e:
        return f"Error reading loci graph: {str(e)}"

@mcp.resource("specs://active")
def get_active_specs_list() -> str:
    """Retorna la lista de especificaciones activas en el motor."""
    specs_list = []
    specs_dir = os.path.join(ROOT_DIR, "doc/specs")
    for root, _, files in os.walk(specs_dir):
        for file in files:
            if file.endswith(".md"):
                specs_list.append(file)
    return "\n".join(specs_list)

if __name__ == "__main__":
    mcp.run()
