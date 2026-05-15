from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from layers.l2_brain.graph_sync_plan import GraphSyncPlan
from layers.l2_brain.graph_sync_ledger import GraphSyncLedger
from layers.l2_brain.vault_embedding_index import VaultEmbeddingIndex
from layers.l2_brain.kuzu_graph_sync_adapter import KuzuGraphSyncAdapter

logger = logging.getLogger(__name__)

class MemoryGraphRuntime:
    """
    [L2_BRAIN] Orchestrator for Memory Graph and Embedding Indexing.
    Connects plans, ledgers, embeddings, and adapters.
    """
    def __init__(
        self,
        ledger: GraphSyncLedger,
        embedding_index: VaultEmbeddingIndex,
        adapter: KuzuGraphSyncAdapter,
        vault_curator: Any = None
    ):
        self.ledger = ledger
        self.embedding_index = embedding_index
        self.adapter = adapter
        self.vault_curator = vault_curator

    def build_plan_from_memory_refs(self, refs: list[dict], mode: str = "dry_run") -> dict:
        plan = GraphSyncPlan.create(mode=mode)
        for ref in refs:
            plan.add_memory_ref(ref)
            
        # Add basic edges between nodes of the same mission
        nodes_by_mission = {}
        for node in plan.nodes:
            if node.mission_id:
                nodes_by_mission.setdefault(node.mission_id, []).append(node.node_id)
        
        for mission_id, node_ids in nodes_by_mission.items():
            if len(node_ids) > 1:
                # Chain them for now as a simple heuristic
                for i in range(len(node_ids) - 1):
                    plan.add_edge(node_ids[i], node_ids[i+1], "BELONGS_TO")

        self.ledger.append_event(plan.sync_id, "GRAPH_SYNC_PLAN_CREATED", {"plan": plan.to_dict()})
        return plan.to_dict()

    def dry_run_sync(self, refs: list[dict]) -> dict:
        plan_dict = self.build_plan_from_memory_refs(refs, mode="dry_run")
        result = self.adapter.dry_run(plan_dict)
        
        self.ledger.append_event(
            plan_dict["sync_id"], 
            "GRAPH_SYNC_DRY_RUN_VALIDATED" if result["status"] == "SUCCESS" else "GRAPH_SYNC_BLOCKED",
            {"result": result}
        )
        return result

    def index_vault_entries(self) -> dict:
        """
        Indices all entries currently in the vault.
        """
        if not self.vault_curator:
            return {"status": "DEGRADED", "error": "Vault curator not available"}
            
        entries = self.vault_curator.list_entries()
        indexed_count = 0
        for entry in entries:
            try:
                self.embedding_index.index_entry(entry)
                indexed_count += 1
            except Exception as e:
                logger.error(f"Failed to index vault entry {entry.get('vault_id')}: {e}")
                
        return {"status": "SUCCESS", "indexed_count": indexed_count}

    def validate_drift(self) -> dict:
        """
        Stub for validating drift between file system and graph.
        """
        return {"status": "SUCCESS", "drift_detected": False, "note": "Drift validation simulated"}
