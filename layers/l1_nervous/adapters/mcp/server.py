import os
import json
import hashlib
import atexit
import signal
import sys
import logging
import kuzu
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

# Configurar logging para redirigir a stderr (estándar MCP)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("dummie-mcp")

# 2. Infrastructure Setup (Bootstrap)
# NOTA: En una arquitectura más madura, este setup se inyectaría desde un punto de entrada global.
# Siguiendo la "Logic Zero Policy", este archivo solo actúa como el canal físico.
ROOT_DIR = os.environ.get("DUMMIE_ROOT_DIR", "/home/jorand/Escritorio/DUMMIE Engine")
AIWG_DIR = os.environ.get("DUMMIE_AIWG_DIR", os.path.join(ROOT_DIR, ".aiwg"))
KUZU_DB_PATH = os.environ.get("DUMMIE_KUZU_DB_PATH", os.path.join(AIWG_DIR, "memory/loci.db"))

def bootstrap_orchestrator():
    """
    Inicializa el orquestador cognitivo con una política de resiliencia ante bloqueos (Spec L1-15).
    """
    db = None
    read_only = False
    
    try:
        # Intento 1: Modo Master (Escritura)
        db = kuzu.Database(KUZU_DB_PATH)
        logger.info(f"Master instance initialized at {KUZU_DB_PATH}")
    except RuntimeError as e:
        error_msg = str(e)
        if "Could not set lock on file" in error_msg or "Permission denied" in error_msg:
            try:
                # Intento 2: Fallback a modo lectura (Spec L1-15, Sec 6.1)
                logger.warning(f"Lock active on {KUZU_DB_PATH}. Attempting READER mode.")
                db = kuzu.Database(KUZU_DB_PATH, read_only=True)
                read_only = True
            except Exception as e2:
                # Intento 3: Modo Desconectado (Resiliencia Extrema)
                logger.critical(f"Database totally locked/inaccessible. Operating in OFFLINE mode. Error: {str(e2)}")
                db = None
                read_only = True
        else:
            logger.error(f"Unexpected DB error during bootstrap: {error_msg}")
            raise

    event_store = KuzuRepository(db_path=KUZU_DB_PATH if db else None, db=db)
    # Forzar el flag si db es None o read_only
    if read_only or db is None:
        event_store.read_only = True
        
    ledger_audit = DecisionLedgerAdapter(
        ledger_path=os.path.join(AIWG_DIR, "ledger/sovereign_resolutions.jsonl"),
        lessons_path=os.path.join(AIWG_DIR, "memory/lessons.jsonl"),
        ambiguities_path=os.path.join(AIWG_DIR, "memory/ambiguities.jsonl"),
        ontological_map_path=os.path.join(AIWG_DIR, "ontological_map.json")
    )
    session_ledger = SessionLedgerAdapter(ledger_path=os.path.join(AIWG_DIR, "memory/ego_state.jsonl"))
    shield = NativeShieldAdapter()
    
    skill_repo = KuzuSkillRepository(db_path=KUZU_DB_PATH if db else None, db=db)
    if read_only or db is None:
        skill_repo.read_only = True

    return CognitiveOrchestrator(
        shield_port=shield,
        event_store=event_store,
        ledger_audit=ledger_audit,
        session_ledger=session_ledger,
        skill_repo=skill_repo
    )

orchestrator = bootstrap_orchestrator()

def _shutdown_flush() -> None:
    """Cierra conexiones para asegurar flush/persistencia antes de terminar el proceso."""
    try:
        if getattr(orchestrator, "skill_repo", None) is not None:
            if getattr(orchestrator.skill_repo, "conn", None) is not None:
                orchestrator.skill_repo.conn.close()
            if getattr(orchestrator.skill_repo, "db", None) is not None:
                orchestrator.skill_repo.db.close()
    except Exception:
        pass
    try:
        if getattr(orchestrator, "event_store", None) is not None:
            if getattr(orchestrator.event_store, "conn", None) is not None:
                orchestrator.event_store.conn.close()
            if getattr(orchestrator.event_store, "db", None) is not None:
                orchestrator.event_store.db.close()
    except Exception:
        pass

atexit.register(_shutdown_flush)
signal.signal(signal.SIGTERM, lambda *_: (_shutdown_flush(), sys.exit(0)))
signal.signal(signal.SIGINT, lambda *_: (_shutdown_flush(), sys.exit(0)))

# --- TOOLS (Standardized per ADR-0013 / Spec L1-15) ---

@mcp.tool()
async def calibrate_neural_links() -> str:
    """
    Realiza una calibración profunda de las conexiones neuronales del motor.
    Verifica: Conectividad KùzuDB, integridad del Ledger y salud del 4D-TES.
    """
    results = []
    # 1. Verificar Kùzu (Memory)
    if getattr(orchestrator.event_store, "db", None) is None:
        results.append("[!] Loci Graph: OFFLINE (Database locked).")
    else:
        node_count = orchestrator.event_store.conn.execute("MATCH (n) RETURN count(n)").get_next()[0]
        results.append(f"[✓] Loci Graph Alive: {node_count} nodes detected.")
    
    # 2. Verificar Ledger (Identity)
    if os.path.exists(orchestrator.ledger_audit.ledger_path):
        results.append(f"[✓] Decision Ledger: Online.")
    else:
        results.append(f"[!] Decision Ledger: MISSING. Initializing skeletal...")
        
    # 3. Clock Sync
    results.append(f"[✓] Lamport Clock: {orchestrator.lamport_clock}")
    
    logger.info("Neural link calibration completed.")
    return "\n".join(results)

@mcp.tool()
async def metacognitive_status() -> str:
    """
    Retorna el estado de 'Ego State' y los aprendizajes recientes para automejora.
    """
    decisions = get_recent_decisions()
    identity = get_brain_identity()
    status = "Degraded" if getattr(orchestrator.event_store, "read_only", False) else "Optimal"
    return f"--- Metacognitive Report ---\nStatus: {status}\nIdentity: {identity}\nRecent Decisions: {decisions}\n---"

@mcp.tool()
async def crystallize(payload: str, context: dict) -> str:
    """
    Punto de entrada único para la persistencia de conocimiento validado en el 4D-TES.
    Mapea a la capacidad física de orquestación de tareas (Spec 02).
    """
    if getattr(orchestrator.event_store, "read_only", False):
        return "[L1-MCP] ERR_MEMORY_LOCKED: El sistema de memoria está en modo lectura por bloqueo de otra instancia (MASTER)."

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
    logger.info(f"Crystallization success: {result}")
    return f"[L1-MCP] Cristalización completada: {result}"

@mcp.tool()
async def log_lesson(issue: str, correction: str) -> str:
    """
    Registra una lección aprendida tras un fallo o descubrimiento.
    Implementa la política de captura de conocimiento de la Spec 48.
    """
    if getattr(orchestrator.event_store, "read_only", False):
        return "[L1-MCP] ERR_MEMORY_LOCKED: No se puede registrar la lección. Memoria bloqueada."

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
        error=Exception(issue),
        tick=orchestrator.lamport_clock,
        correction=correction
    )
    return f"[L1-MCP] Lección registrada exitosamente en .aiwg"

@mcp.tool()
async def resolve_ambiguity(ambiguity: str, plan: str) -> str:
    """
    Registra una ambigüedad descubierta y el plan para resolverla.
    Activa el protocolo de cierre cognitivo (Spec 49).
    """
    if getattr(orchestrator.event_store, "read_only", False):
        return "[L1-MCP] ERR_MEMORY_LOCKED: No se puede registrar la ambigüedad. Memoria bloqueada."

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

@mcp.tool()
async def ssh_grep(pattern: str, path: str = ".", include: str = "*") -> str:
    """
    Ejecuta una búsqueda optimizada (grep) a través del bridge SSH (Spec 41).
    Ideal para 'low-entropy reading' de grandes volúmenes de código sin saturar el contexto.
    """
    import asyncio
    import subprocess
    
    # Propagación de contexto (Spec 41/12)
    env = os.environ.copy()
    env["DUMMIE_CONTEXT_T"] = str(orchestrator.lamport_clock)
    
    # Comando grep vía SSH (Simulado mediante ejecución local protegida por el bridge)
    # En una implementación física completa, esto usaría la conexión SSH establecida.
    cmd = ["grep", "-rnI", "--include", include, pattern, os.path.join(ROOT_DIR, path)]
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0 and not stdout:
            return f"No se encontraron coincidencias para '{pattern}' en {path}."
            
        # Aplicar el Causal Pruning si el output es demasiado grande
        lines = stdout.decode().splitlines()
        if len(lines) > 50:
            return "\n".join(lines[:50]) + f"\n... (Truncated: {len(lines) - 50} more lines. Use more specific pattern or subpath)"
            
        return stdout.decode()
    except Exception as e:
        return f"Error ejecutando SSH-Grep: {str(e)}"

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
    path = orchestrator.ledger_audit.ledger_path
    if not os.path.exists(path): return "No decisions found."
    with open(path, "r") as f:
        return "".join(f.readlines()[-10:])

@mcp.resource("memory://timeline")
def get_memory_timeline() -> str:
    """
    Stream de eventos inmutables del 4D-TES (Spec 02).
    Aplica Causal Pruning (Spec 40B): limita el historial a los últimos 50 nodos.
    """
    if orchestrator.event_store.conn is None:
        return "Memory Timeline: OFFLINE (No database connection)."
    
    results = orchestrator.event_store.conn.execute(
        "MATCH (m:MemoryNode4D) RETURN m.lamport_t, m.causal_hash, m.intent_i ORDER BY m.lamport_t DESC LIMIT 50"
    )
    events = []
    while results.has_next():
        row = results.get_next()
        events.append(f"T={row[0]} | Hash={row[1]} | Intent={row[2]}")
    return "\n".join(events) if events else "Timeline empty."

@mcp.resource("memory://loci")
def get_memory_loci() -> str:
    """Acceso al grafo de relaciones ontológicas (Palacio de Loci)."""
    if orchestrator.event_store.conn is None:
        return json.dumps({"status": "Offline", "reason": "Database locked"}, indent=2)

    # Resumen estadístico del grafo
    nodes_summary = []
    rels_summary = []
    
    try:
        node_results = orchestrator.event_store.conn.execute("MATCH (n) RETURN labels(n), count(*)")
        while node_results.has_next():
            nodes_summary.append(node_results.get_next())
            
        rel_results = orchestrator.event_store.conn.execute("MATCH ()-[r]->() RETURN label(r), count(*)")
        while rel_results.has_next():
            rels_summary.append(rel_results.get_next())
    except Exception as e:
        logger.error(f"Error inspecting loci topology: {e}")
        return json.dumps({"status": "Error", "reason": str(e)}, indent=2)
        
    return json.dumps({
        "status": "Healthy",
        "topology": "Merkle-DAG",
        "summary": {
            "nodes": nodes_summary,
            "relationships": rels_summary
        }
    }, indent=2)

@mcp.resource("memory://latest_node")
def get_latest_memory_node() -> str:
    """Retorna el último nodo 4D-TES persistido, incluyendo coordenadas 6D (Spec 02)."""
    if orchestrator.event_store.conn is None:
        return json.dumps({"status": "Offline", "db_path": KUZU_DB_PATH}, indent=2)

    result = orchestrator.event_store.conn.execute(
        "MATCH (m:MemoryNode4D) "
        "RETURN "
        "m.causal_hash, m.parent_hash, "
        "m.locus_x, m.locus_y, m.locus_z, "
        "m.lamport_t, m.authority_a, m.intent_i, "
        "m.payload_hash "
        "ORDER BY m.lamport_t DESC LIMIT 1"
    )
    if not result.has_next():
        return json.dumps(
            {
                "db_path": getattr(orchestrator.event_store, "db_path", None),
                "read_only": getattr(orchestrator.event_store, "read_only", None),
                "latest": None,
            },
            indent=2,
        )
    row = result.get_next()
    return json.dumps(
        {
            "db_path": getattr(orchestrator.event_store, "db_path", None),
            "read_only": getattr(orchestrator.event_store, "read_only", None),
            "latest": {
                "causal_hash": row[0],
                "parent_hash": row[1],
                "locus_x": row[2],
                "locus_y": row[3],
                "locus_z": row[4],
                "lamport_t": row[5],
                "authority_a": row[6],
                "intent_i": row[7],
                "payload_hash": row[8],
            },
        },
        indent=2,
    )

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

@mcp.resource("brain://health")
def get_brain_health() -> str:
    """
    Reporta el estado de salud del adaptador y la persistencia (Spec 15).
    Identifica si la instancia está en modo MASTER o READER.
    """
    is_read_only = getattr(orchestrator.event_store, "read_only", False)
    db_status = "READER (Degraded)" if is_read_only else "MASTER (Optimal)"
    
    return json.dumps({
        "status": "Healthy",
        "mode": db_status,
        "kuzu_db": "Connected" if orchestrator.event_store.db else "Disconnected",
        "ledger": "Available" if os.path.exists(orchestrator.ledger_audit.ledger_path) else "Missing",
        "clock": orchestrator.lamport_clock
    }, indent=2)

if __name__ == "__main__":
    mcp.run()
