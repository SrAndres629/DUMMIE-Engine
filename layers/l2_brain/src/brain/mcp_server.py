"""
DUMMIE Engine - L2 Brain: MCP Server para Motor de Memoria Persistente 4D-TES
=============================================================================
Spec-Driven Development (SDD) - Namespace: io.dummie.v2.memory.mcp

Este servidor MCP expone el motor de memoria inmutable 4D-TES (Spec 02),
el modelo 6D-Context (Spec 12), el Decision Ledger (Spec 34), el Session
Ledger (Spec 36) y la Cristalización Procedimental (Spec 38) como
herramientas MCP estándar.

Transporte: stdio (compatible con Antigravity, DUMMIE Engine, Claude, etc.)
"""
import os
import sys
import json
import hashlib
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ============================================================================
# Configuration
# ============================================================================
PROJECT_ROOT = os.environ.get(
    "DUMMIE_PROJECT_ROOT",
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
)

DB_PATH = os.environ.get(
    "DUMMIE_MEMORY_DB_PATH",
    os.path.join(PROJECT_ROOT, ".aiwg", "memory", "loci.db")
)

LEDGER_PATH = os.environ.get(
    "DUMMIE_LEDGER_PATH",
    os.path.join(PROJECT_ROOT, ".aiwg", "memory", "decisions.jsonl")
)

# Ensure PYTHONPATH includes src
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# ============================================================================
# Logging
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stderr  # MCP uses stdout for protocol; logs go to stderr
)
logger = logging.getLogger("dummie.mcp.memory")

# ============================================================================
# Lazy Infrastructure Initialization
# ============================================================================
_kuzu_repo = None
_skill_repo = None
_ledger_adapter = None
_orchestrator = None


def _get_kuzu_repo():
    """Lazy singleton for KuzuRepository."""
    global _kuzu_repo
    if _kuzu_repo is None:
        from brain.infrastructure.adapters.kuzu_repository import KuzuRepository
        logger.info(f"Initializing KuzuRepository at: {DB_PATH}")
        _kuzu_repo = KuzuRepository(db_path=DB_PATH)
    return _kuzu_repo


def _get_skill_repo():
    """Lazy singleton for KuzuSkillRepository."""
    global _skill_repo
    if _skill_repo is None:
        from brain.infrastructure.adapters.kuzu_repository import KuzuSkillRepository
        _skill_repo = KuzuSkillRepository(_get_kuzu_repo())
    return _skill_repo


def _get_ledger_adapter():
    """Lazy singleton for DecisionLedgerAdapter."""
    global _ledger_adapter
    if _ledger_adapter is None:
        from brain.infrastructure.adapters.ledger_adapter import DecisionLedgerAdapter
        logger.info(f"Initializing DecisionLedgerAdapter at: {LEDGER_PATH}")
        _ledger_adapter = DecisionLedgerAdapter(ledger_path=LEDGER_PATH)
    return _ledger_adapter


def _get_orchestrator():
    """Lazy singleton for CognitiveOrchestrator."""
    global _orchestrator
    if _orchestrator is None:
        from brain.infrastructure.adapters.shield_adapter import NativeShieldAdapter
        from brain.application.use_cases.orchestrator import CognitiveOrchestrator
        _orchestrator = CognitiveOrchestrator(
            shield_port=NativeShieldAdapter(),
            event_store=_get_kuzu_repo(),
            ledger_audit=_get_ledger_adapter(),
            skill_repo=_get_skill_repo()
        )
    return _orchestrator


# ============================================================================
# MCP Server Definition
# ============================================================================
mcp = FastMCP(
    name="dummie-memory",
    instructions=(
        "DUMMIE Engine L2 Brain - Motor de Memoria Persistente 4D-TES. "
        "Provides immutable causal memory (Merkle-DAG), 6D spatial-temporal "
        "context indexing, decision ledger auditing, and procedural memory "
        "crystallization via MCP tools."
    ),
)


# ============================================================================
# TOOL: memory_append
# ============================================================================
@mcp.tool(
    name="memory_append",
    description=(
        "Append a new immutable memory node to the 4D-TES Merkle-DAG. "
        "Automatically chains to the current head, computes causal hashes, "
        "and increments the Lamport clock. Returns the new node's causal hash."
    ),
)
def memory_append(
    payload_json: str,
    locus_x: str = "agent.session",
    locus_y: str = "task.execution",
    locus_z: str = "entity.atomic",
    intent: str = "OBSERVATION",
    authority: str = "AGENT",
) -> str:
    """
    Args:
        payload_json: JSON string with the data to persist (observations, decisions, etc.)
        locus_x: Bounded Context identifier (e.g., 'sw.plant.coder')
        locus_y: Aggregate Root identifier (e.g., 'task.execution')
        locus_z: Atomic Entity identifier (e.g., 'entity.file')
        intent: Intent type: OBSERVATION, MUTATION, RESOLUTION, CRYSTALLIZATION
        authority: Authority level: AGENT, ENGINEER, ARCHITECT, OVERSEER, HUMAN
    """
    from brain.domain.context.models import SixDimensionalContext, AuthorityLevel, IntentType
    from brain.domain.memory.models import MemoryNode4DTES

    repo = _get_kuzu_repo()

    # Get current head for chaining
    last_hash = repo.get_last_leaf_hash(locus_x=locus_x)
    last_node = repo.get_by_hash(last_hash) if last_hash != "GENESIS" else None
    current_tick = (last_node.context.lamport_t + 1) if last_node else 1

    # Map string enums
    try:
        intent_enum = IntentType(intent)
    except ValueError:
        intent_enum = IntentType.OBSERVATION

    try:
        authority_enum = AuthorityLevel(authority)
    except ValueError:
        authority_enum = AuthorityLevel.AGENT

    # Build 6D Context
    context = SixDimensionalContext(
        locus_x=locus_x,
        locus_y=locus_y,
        locus_z=locus_z,
        lamport_t=current_tick,
        authority_a=authority_enum,
        intent_i=intent_enum,
    )

    # Generate node with causal hash
    payload_bytes = payload_json.encode("utf-8")
    node = MemoryNode4DTES.generate(
        parent_hash=last_hash,
        context=context,
        payload=payload_bytes,
    )

    # Persist
    result = repo.append(node)
    if not result:
        return json.dumps({"error": "Failed to persist node to KuzuDB", "success": False})

    logger.info(f"Node appended: {node.causal_hash[:16]}... (tick={current_tick}, parent={last_hash[:16]}...)")

    return json.dumps({
        "success": True,
        "causal_hash": node.causal_hash,
        "parent_hash": last_hash,
        "lamport_t": current_tick,
        "locus_x": locus_x,
        "intent": intent,
    })


# ============================================================================
# TOOL: memory_get_node
# ============================================================================
@mcp.tool(
    name="memory_get_node",
    description="Retrieve a specific memory node by its causal hash from the 4D-TES Merkle-DAG.",
)
def memory_get_node(causal_hash: str) -> str:
    """
    Args:
        causal_hash: The SHA-256 causal hash of the node to retrieve.
    """
    repo = _get_kuzu_repo()
    node = repo.get_by_hash(causal_hash)
    if not node:
        return json.dumps({"error": f"Node not found: {causal_hash}", "found": False})

    payload_str = node.payload.decode("utf-8", errors="replace")

    return json.dumps({
        "found": True,
        "causal_hash": node.causal_hash,
        "parent_hash": node.parent_hash,
        "payload": payload_str,
        "payload_hash": node.payload_hash,
        "context": {
            "locus_x": node.context.locus_x,
            "locus_y": node.context.locus_y,
            "locus_z": node.context.locus_z,
            "lamport_t": node.context.lamport_t,
            "authority_a": node.context.authority_a.value if hasattr(node.context.authority_a, 'value') else str(node.context.authority_a),
            "intent_i": node.context.intent_i.value if hasattr(node.context.intent_i, 'value') else str(node.context.intent_i),
        },
    })


# ============================================================================
# TOOL: memory_get_chain
# ============================================================================
@mcp.tool(
    name="memory_get_chain",
    description=(
        "Reconstruct the causal chain (Merkle-DAG ancestry) backwards from a leaf node. "
        "Returns nodes ordered by Lamport tick ascending."
    ),
)
def memory_get_chain(leaf_hash: str, depth: int = 30) -> str:
    """
    Args:
        leaf_hash: The causal hash of the leaf node to start from.
        depth: Maximum number of ancestors to retrieve (default: 30).
    """
    repo = _get_kuzu_repo()
    chain = repo.get_causal_chain(leaf_hash, depth=depth)

    if not chain:
        return json.dumps({"error": f"No chain found from: {leaf_hash}", "nodes": []})

    nodes = []
    for node in chain:
        nodes.append({
            "causal_hash": node.causal_hash,
            "parent_hash": node.parent_hash,
            "lamport_t": node.context.lamport_t,
            "locus_x": node.context.locus_x,
            "intent": node.context.intent_i.value if hasattr(node.context.intent_i, 'value') else str(node.context.intent_i),
        })

    return json.dumps({"chain_length": len(nodes), "nodes": nodes})


# ============================================================================
# TOOL: memory_get_head
# ============================================================================
@mcp.tool(
    name="memory_get_head",
    description=(
        "Get the causal hash of the most recent node (head) in the Merkle-DAG. "
        "Returns 'GENESIS' if the memory is empty."
    ),
)
def memory_get_head(locus_x: Optional[str] = None) -> str:
    """
    Args:
        locus_x: Optional bounded context filter. If provided, returns the head for that specific context.
    """
    repo = _get_kuzu_repo()
    head = repo.get_last_leaf_hash(locus_x=locus_x)

    result = {"head_hash": head, "is_genesis": head == "GENESIS"}

    if head != "GENESIS":
        node = repo.get_by_hash(head)
        if node:
            result["lamport_t"] = node.context.lamport_t
            result["locus_x"] = node.context.locus_x

    return json.dumps(result)


# ============================================================================
# TOOL: memory_search
# ============================================================================
@mcp.tool(
    name="memory_search",
    description=(
        "Search memory nodes by 6D context dimensions (locus_x, locus_y, locus_z, intent). "
        "Returns matching nodes ordered by Lamport tick."
    ),
)
def memory_search(
    locus_x: Optional[str] = None,
    locus_y: Optional[str] = None,
    intent: Optional[str] = None,
    limit: int = 20,
) -> str:
    """
    Args:
        locus_x: Filter by Bounded Context ID.
        locus_y: Filter by Aggregate Root ID.
        intent: Filter by intent type (OBSERVATION, MUTATION, RESOLUTION, CRYSTALLIZATION).
        limit: Maximum number of results (default: 20).
    """
    repo = _get_kuzu_repo()

    # Build dynamic query
    conditions = []
    params = {}
    if locus_x:
        conditions.append("m.locus_x = $lx")
        params["lx"] = locus_x
    if locus_y:
        conditions.append("m.locus_y = $ly")
        params["ly"] = locus_y
    if intent:
        conditions.append("m.intent_i = $ii")
        params["ii"] = intent

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"MATCH (m:MemoryNode4D){where_clause} RETURN m.causal_hash, m.parent_hash, m.locus_x, m.locus_y, m.locus_z, m.lamport_t, m.intent_i ORDER BY m.lamport_t DESC LIMIT {limit}"

    try:
        result = repo.conn.execute(query, params)
        nodes = []
        while result.has_next():
            row = result.get_next()
            nodes.append({
                "causal_hash": row[0],
                "parent_hash": row[1],
                "locus_x": row[2],
                "locus_y": row[3],
                "locus_z": row[4],
                "lamport_t": row[5],
                "intent": row[6],
            })
        return json.dumps({"count": len(nodes), "nodes": nodes})
    except Exception as e:
        return json.dumps({"error": str(e), "count": 0, "nodes": []})


# ============================================================================
# TOOL: ledger_record
# ============================================================================
@mcp.tool(
    name="ledger_record",
    description=(
        "Record an immutable decision in the Decision Ledger (Spec 34). "
        "Creates an audit trail with causal context and cryptographic witness."
    ),
)
def ledger_record(
    decision_id: str,
    rationale: str,
    impact_blast_radius: str = "local.component",
    locus_x: str = "agent.session",
    target_causal_hash: str = "GENESIS",
    witness_hash: str = "PENDING_SIGNATURE",
) -> str:
    """
    Args:
        decision_id: Unique identifier for the decision.
        rationale: Human-readable explanation of the decision.
        impact_blast_radius: Scope of impact (e.g., 'local.component', 'domain.procedural').
        locus_x: Bounded Context where the decision applies.
        target_causal_hash: The 4D-TES node this decision relates to.
        witness_hash: Cryptographic signature from the auditor.
    """
    from brain.domain.context.models import SixDimensionalContext, AuthorityLevel, IntentType
    from brain.domain.governance.models import DecisionRecord

    ledger = _get_ledger_adapter()

    context = SixDimensionalContext(
        locus_x=locus_x,
        locus_y="decision.ledger",
        locus_z="record.atomic",
        lamport_t=0,  # Will be set by caller if needed
        authority_a=AuthorityLevel.ARCHITECT,
        intent_i=IntentType.RESOLUTION,
    )

    record = DecisionRecord(
        decision_id=decision_id,
        rationale=rationale,
        impact_blast_radius=impact_blast_radius,
        context=context,
        target_causal_hash=target_causal_hash,
        witness_hash=witness_hash,
    )

    success = ledger.record_decision(record)

    return json.dumps({
        "success": bool(success),
        "decision_id": decision_id,
        "rationale": rationale,
    })


# ============================================================================
# TOOL: ledger_get_certainty
# ============================================================================
@mcp.tool(
    name="ledger_get_certainty",
    description=(
        "Calculate the ontological certainty score for a bounded context (locus_x). "
        "Returns the ratio of validated decisions to total decisions."
    ),
)
def ledger_get_certainty(locus_x: str) -> str:
    """
    Args:
        locus_x: The Bounded Context ID to calculate certainty for.
    """
    ledger = _get_ledger_adapter()
    certainty = ledger.get_certainty_for_locus(locus_x)

    return json.dumps({
        "locus_x": locus_x,
        "certainty_score": certainty.certainty_score,
        "tests_passing": certainty.tests_passing,
        "unverified_mutations": certainty.unverified_mutations,
        "is_terra_incognita": certainty.is_terra_incognita,
    })


# ============================================================================
# TOOL: skill_save
# ============================================================================
@mcp.tool(
    name="skill_save",
    description=(
        "Save a crystallized procedural skill (Spec 38). "
        "Links the skill to its source 4D-TES nodes for causal provenance."
    ),
)
def skill_save(
    skill_id: str,
    yaml_payload: str,
    source_causal_hashes: str = "[]",
) -> str:
    """
    Args:
        skill_id: Unique identifier for the skill.
        yaml_payload: The YAML content of the skill specification.
        source_causal_hashes: JSON array of causal hashes from the 4D-TES nodes that originated this skill.
    """
    from brain.domain.memory.models import CrystallizedSkill

    skill_repo = _get_skill_repo()

    try:
        hashes = json.loads(source_causal_hashes)
    except json.JSONDecodeError:
        hashes = []

    # Compute cryptographic seal
    skill_seed = f"{yaml_payload}{''.join(hashes)}".encode("utf-8")
    skill_hash = hashlib.sha256(skill_seed).hexdigest()

    skill = CrystallizedSkill(
        skill_id=skill_id,
        yaml_payload=yaml_payload,
        source_causal_hashes=hashes,
        skill_hash=skill_hash,
    )

    skill_repo.save_skill(skill)

    return json.dumps({
        "success": True,
        "skill_id": skill_id,
        "skill_hash": skill_hash,
        "provenance_count": len(hashes),
    })


# ============================================================================
# TOOL: skill_get
# ============================================================================
@mcp.tool(
    name="skill_get",
    description="Retrieve a crystallized skill by its ID, including causal provenance links.",
)
def skill_get(skill_id: str) -> str:
    """
    Args:
        skill_id: The unique identifier of the skill to retrieve.
    """
    skill_repo = _get_skill_repo()
    skill = skill_repo.get_skill_by_id(skill_id)

    if not skill:
        return json.dumps({"found": False, "skill_id": skill_id})

    return json.dumps({
        "found": True,
        "skill_id": skill.skill_id,
        "yaml_payload": skill.yaml_payload,
        "skill_hash": skill.skill_hash,
        "source_causal_hashes": skill.source_causal_hashes,
    })


# ============================================================================
# TOOL: brain_process_task
# ============================================================================
@mcp.tool(
    name="brain_process_task",
    description=(
        "Submit a task to the L2 Brain Cognitive Orchestrator. "
        "Executes the full cycle: Shield audit -> 4D-TES chaining -> "
        "Decision ledger -> Crystallization check. Returns validation status."
    ),
)
async def brain_process_task(payload: str) -> str:
    """
    Args:
        payload: The task description or payload to process.
    """
    orchestrator = _get_orchestrator()
    try:
        result = await orchestrator.handle_task(payload)
        return json.dumps({"success": True, "status": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


# ============================================================================
# TOOL: brain_status
# ============================================================================
@mcp.tool(
    name="brain_status",
    description=(
        "Get the current status of the DUMMIE Engine L2 Brain memory engine. "
        "Returns head hash, node count, and system information."
    ),
)
def brain_status() -> str:
    """Returns comprehensive status of the memory engine."""
    repo = _get_kuzu_repo()

    # Get head
    head = repo.get_last_leaf_hash()

    # Count nodes
    try:
        result = repo.conn.execute("MATCH (m:MemoryNode4D) RETURN count(m)")
        node_count = result.get_next()[0] if result.has_next() else 0
    except Exception:
        node_count = -1

    # Count skills
    try:
        result = repo.conn.execute("MATCH (s:Skill) RETURN count(s)")
        skill_count = result.get_next()[0] if result.has_next() else 0
    except Exception:
        skill_count = -1

    # Head node details
    head_info = {}
    if head != "GENESIS":
        node = repo.get_by_hash(head)
        if node:
            head_info = {
                "lamport_t": node.context.lamport_t,
                "locus_x": node.context.locus_x,
                "intent": node.context.intent_i.value if hasattr(node.context.intent_i, 'value') else str(node.context.intent_i),
            }

    # Ledger stats
    ledger = _get_ledger_adapter()
    ledger_exists = os.path.exists(ledger.ledger_path)
    ledger_entries = 0
    if ledger_exists:
        try:
            with open(ledger.ledger_path, "r") as f:
                ledger_entries = sum(1 for _ in f)
        except Exception:
            pass

    return json.dumps({
        "engine": "DUMMIE Engine L2 Brain - 4D-TES Memory",
        "version": "2.2.0",
        "db_path": DB_PATH,
        "ledger_path": LEDGER_PATH,
        "head_hash": head,
        "is_genesis": head == "GENESIS",
        "head_info": head_info,
        "total_nodes": node_count,
        "total_skills": skill_count,
        "ledger_entries": ledger_entries,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


# ============================================================================
# RESOURCE: memory://status
# ============================================================================
@mcp.resource("memory://status", name="Memory Engine Status", description="Current state of the 4D-TES memory engine")
def resource_status() -> str:
    return brain_status()


# ============================================================================
# Entry Point
# ============================================================================
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("DUMMIE Engine L2 Brain - MCP Memory Server Starting")
    logger.info(f"  DB Path:     {DB_PATH}")
    logger.info(f"  Ledger Path: {LEDGER_PATH}")
    logger.info("=" * 60)
    mcp.run(transport="stdio")
