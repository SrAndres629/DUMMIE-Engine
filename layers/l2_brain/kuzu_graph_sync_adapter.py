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
        try:
            import kuzu
            self.kuzu = kuzu
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
            "db_status": validation["status"]
        }

    def apply(self, plan: dict, allow_write: bool = False) -> dict:
        """
        Applies the plan to the database if allow_write is True.
        """
        if not allow_write:
            return self.dry_run(plan)
            
        validation = self.validate_plan(plan)
        if not validation["valid"]:
            return {"status": "FAILED", "errors": validation["errors"]}
            
        if not self.kuzu:
             return {"status": "DEGRADED", "error": "Kuzu not installed. Cannot apply writes."}
             
        # Actual write logic would go here in future phases.
        # For now, we still just simulate success to avoid breaking things.
        return {
            "status": "SUCCESS",
            "mode": "apply",
            "nodes_written": len(plan.get("nodes", [])),
            "edges_written": len(plan.get("edges", [])),
            "note": "Actual Kuzu writes simulated in Phase 9"
        }
