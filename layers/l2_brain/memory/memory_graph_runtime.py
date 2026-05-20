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
        
        # 1. Create Nodes
        node_map = {} # memory_ref_id -> node_id
        for ref in refs:
            plan.add_memory_ref(ref)
            node = plan.nodes[-1]
            node_map[ref.get("memory_ref_id")] = node.node_id
            
        # 2. Add Causal/Relational Edges
        for ref in refs:
            source_id = node_map.get(ref.get("memory_ref_id"))
            rtype = ref.get("ref_type")
            
            # LearningEpisode relations
            if rtype == "learning_episode":
                # PRODUCED -> VaultEntry
                for vref in ref.get("vault_refs", []):
                    target_id = node_map.get(vref)
                    if target_id:
                        plan.add_edge(source_id, target_id, "PRODUCED")
                
                # SUMMARIZES -> Workbench
                wb_ref = ref.get("workbench_ref")
                if wb_ref:
                    target_id = node_map.get(wb_ref)
                    if target_id:
                        plan.add_edge(source_id, target_id, "SUMMARIZES")
                
                # COSTED_BY -> TokenLedger (heuristics based on mission)
                for other in refs:
                    if other.get("ref_type") == "token_ledger" and other.get("mission_id") == ref.get("mission_id"):
                        target_id = node_map.get(other.get("memory_ref_id"))
                        if target_id:
                             plan.add_edge(source_id, target_id, "COSTED_BY")

            # VaultEntry relations
            if rtype == "vault_entry":
                # DERIVED_FROM -> Workbench
                for other in refs:
                    if other.get("ref_type") == "workbench" and other.get("mission_id") == ref.get("mission_id"):
                         target_id = node_map.get(other.get("memory_ref_id"))
                         if target_id:
                              plan.add_edge(source_id, target_id, "DERIVED_FROM")

            # PhaseEvent relations
            if rtype == "phase_event":
                # FOLLOWS -> PhaseEvent (simplified: follows previous in list if same mission)
                # In real 4D-TES we use sequence numbers.
                pass

        # 3. Add BELONGS_TO Mission (General heuristic)
        for node in plan.nodes:
            if node.mission_id:
                # We don't have a Mission node in the refs usually, 
                # but we can create a virtual mission node if needed.
                # For now, we just link to other nodes in same mission if no better link exists.
                pass

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
        Validates drift between file system, embedding index, and latest graph plan.
        """
        drift = {
            "missing_embedding_entries": [],
            "orphan_embedding_entries": [],
            "missing_graph_nodes": [],
            "stale_hashes": [],
            "drift_detected": False
        }
        
        # 1. Load data
        vault_entries = self.vault_curator.list_entries() if self.vault_curator else []
        embedding_entries = self.embedding_index.get_all_entries()
        latest_plan = self.ledger.get_latest_plan() or {"nodes": []}
        graph_nodes = {n["memory_ref_id"]: n for n in latest_plan.get("nodes", [])}
        
        # 2. Check Vault vs Embedding
        vault_ids = {e["vault_id"]: e for e in vault_entries}
        for vid, v_entry in vault_ids.items():
            if vid not in embedding_entries:
                drift["missing_embedding_entries"].append(vid)
            else:
                if v_entry["content_hash"] != embedding_entries[vid]["content_hash"]:
                    drift["stale_hashes"].append(f"embedding:{vid}")

        for vid in embedding_entries:
            if vid not in vault_ids:
                drift["orphan_embedding_entries"].append(vid)

        # 3. Check Vault vs Graph
        for vid, v_entry in vault_ids.items():
            # Vault IDs are usually the memory_ref_id or derived from it.
            # In our current impl, vault_id is used as memory_ref_id for vault entries.
            if v_entry.get("vault_id") not in graph_nodes:
                 drift["missing_graph_nodes"].append(vid)
            else:
                if v_entry["content_hash"] != graph_nodes[v_entry["vault_id"]]["content_hash"]:
                    drift["stale_hashes"].append(f"graph:{vid}")

        drift["drift_detected"] = any([
            drift["missing_embedding_entries"],
            drift["orphan_embedding_entries"],
            drift["missing_graph_nodes"],
            drift["stale_hashes"]
        ])
        
        return drift
