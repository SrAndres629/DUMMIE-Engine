from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

class KuzuGraphSyncAdapter:
    """
    [L2_BRAIN] Adapter for Kuzu/4D-TES synchronization.
    Provides dry-run and safe apply capabilities.
    """
    def __init__(self, db_path: str = ".aiwg/kuzu.db"):
        self.db_path = db_path
        self.kuzu = None
        self.repo = None
        try:
            import kuzu
            self.kuzu = kuzu
            try:
                from layers.l2_brain.infrastructure.adapters.kuzu import KuzuRepository
            except ImportError:
                from infrastructure.adapters.kuzu import KuzuRepository
            self.repo = KuzuRepository(db_path=self.db_path)
        except ImportError:
            logger.warning("Kuzu not installed. Graph sync will run in DEGRADED mode.")

    def validate_plan(self, plan: dict) -> dict:
        """
        Validates the plan schema and safety.
        """
        errors = []
        if not plan.get("sync_id"):
            errors.append("Missing sync_id")
        if plan.get("blocked"):
            errors.append("Plan is blocked by safety checks")
        
        nodes = plan.get("nodes", [])
        edges = plan.get("edges", [])
        
        if not nodes and not edges:
            errors.append("Plan contains no nodes or edges")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "status": "READY" if self.kuzu else "DEGRADED"
        }

    def dry_run(self, plan: dict) -> dict:
        """
        Performs a dry-run of the plan.
        """
        validation = self.validate_plan(plan)
        if not validation["valid"]:
            return {"status": "FAILED", "errors": validation["errors"]}
            
        return {
            "status": "SUCCESS",
            "mode": "dry_run",
            "nodes_planned": len(plan.get("nodes", [])),
            "edges_planned": len(plan.get("edges", [])),
            "writes_performed": False,
            "simulation": True,
            "db_status": validation["status"]
        }

    def apply(self, plan: dict, allow_write: bool = False) -> dict:
        """
        Applies the plan to the database if allow_write is True.
        """
        if not allow_write:
            res = self.dry_run(plan)
            res["mode"] = "dry_run_refused_write"
            return res
            
        validation = self.validate_plan(plan)
        if not validation["valid"]:
            return {"status": "FAILED", "errors": validation["errors"]}
            
        if not self.kuzu or not self.repo:
             return {"status": "DEGRADED", "error": "Kuzu or Repository not initialized. Cannot apply writes.", "writes_performed": False}
             
        try:
            import json
            import re
            import hashlib
            try:
                from layers.l2_brain.l2_memory_models import MemoryNode4D, AuthorityLevel, IntentType
            except ImportError:
                from layers.l2_brain.l2_memory_models import MemoryNode4D, AuthorityLevel, IntentType
                
            nodes_written = 0
            id_to_hash = {}
            
            # Map graph nodes to MemoryNode4D
            for gnode in plan.get("nodes", []):
                node_id = gnode.get("node_id")
                # Determine parents from edges
                parents = []
                for edge in plan.get("edges", []):
                    if edge.get("target") == node_id:
                        source_id = edge.get("source")
                        # Use already computed causal hash of parent if available
                        parent_hash = id_to_hash.get(source_id)
                        if parent_hash:
                            parents.append(parent_hash)
                        else:
                            source_node = next((n for n in plan.get("nodes", []) if n.get("node_id") == source_id), None)
                            if source_node and source_node.get("content_hash") and re.match(r"^[a-f0-9]{64}$", source_node.get("content_hash")):
                                parents.append(source_node.get("content_hash"))
                            else:
                                parents.append(source_id)
                
                if not parents:
                    parents = ["GENESIS"]
                    
                payload_dict = {
                    "node_id": node_id,
                    "node_type": gnode.get("node_type"),
                    "memory_ref_id": gnode.get("memory_ref_id"),
                    "mission_id": gnode.get("mission_id"),
                    "phase_id": gnode.get("phase_id"),
                    "properties": gnode.get("properties", {})
                }
                payload = json.dumps(payload_dict)
                
                node = MemoryNode4D.from_intent_context(
                    parent_hashes=parents,
                    locus_x=gnode.get("mission_id") or "sw.strategy.discovery",
                    locus_y=gnode.get("phase_id") or "L1_TRANSPORT",
                    locus_z=gnode.get("node_type") or "GenericNode",
                    lamport_t=0,
                    authority_a=AuthorityLevel.AGENT,
                    intent_i=IntentType.CRYSTALLIZATION,
                    payload=payload
                )
                
                self.repo.create_memory_node(node)
                id_to_hash[node_id] = node.causal_hash
                nodes_written += 1
                
            return {
                "status": "SUCCESS",
                "mode": "apply",
                "nodes_planned": len(plan.get("nodes", [])),
                "edges_planned": len(plan.get("edges", [])),
                "writes_performed": True,
                "simulation": False,
                "db_status": "READY",
                "nodes_written": nodes_written,
                "id_to_hash": id_to_hash
            }
        except Exception as e:
            logger.error(f"Error executing real write to Kuzu: {e}")
            return {
                "status": "FAILED",
                "error": f"Kuzu write failed: {e}",
                "writes_performed": False
            }
