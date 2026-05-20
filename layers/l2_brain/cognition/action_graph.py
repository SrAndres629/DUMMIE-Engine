# Spec: 166_l2_brain_organ_migration_contract
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("brain.action_graph")

@dataclass
class ActionNode:
    action_id: str
    saga_id: str
    model_id: str
    action_type: str  # READ, WRITE, RUN_CMD, REASON
    target: str       # File path or tool name
    description: str
    timestamp: str = ""

class ActionGraph:
    """
    [L2_BRAIN] Grafo de acciones trazables.
    Registra quién hizo qué y por qué, persistiendo en 4D-TES.
    """
    def __init__(self, kuzu_repo: Any):
        self.kuzu_repo = kuzu_repo

    async def record_action(self, node: ActionNode):
        from models import MemoryNode4D
        node.timestamp = datetime.now().isoformat()
        logger.info(f"ActionGraph: Recording {node.action_type} by {node.model_id} on {node.target}")
        
        # Persistencia en 4D-TES
        if self.kuzu_repo:
            try:
                # Usar el factory method correcto
                mem_node = MemoryNode4D.from_intent_context(
                    payload=node.description,
                    locus_x="action_graph",
                    locus_y="L2_BRAIN",
                    locus_z="PERSISTENCE",
                    authority_a=node.model_id,
                    intent_i="ACTION_EXECUTION",
                    parent_hash=node.saga_id if node.saga_id != "unknown" else "GENESIS",
                    action_type=node.action_type,
                    target=node.target,
                    action_id=node.action_id
                )
                self.kuzu_repo.create_memory_node(mem_node)
            except Exception as e:
                logger.error(f"Failed to record action in graph: {e}")
