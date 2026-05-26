from __future__ import annotations

import logging
from typing import Any
from layers.l2_brain.domain.authority import AuthorityLevel

logger = logging.getLogger(__name__)


class KuzuGraphSyncAdapter:
    """
    [L2_BRAIN] Adapter for Kuzu/4D-TES synchronization.
    MANDATO SOBERANO: allow_write es True por defecto para niveles autorizados.
    """

    def __init__(self, db_path: str = ".aiwg/kuzu.db"):
        self.db_path = db_path
        self.kuzu = None
        self.repo = None
        try:
            import kuzu

            self.kuzu = kuzu
            from layers.l2_brain.infrastructure.kuzu import KuzuRepository

            self.repo = KuzuRepository(db_path=self.db_path)
            logger.info(f"KuzuGraphSyncAdapter: SVRN_READY at {db_path}")
        except ImportError:
            logger.warning(
                "Kuzu not installed or Repository missing. Graph sync will run in DEGRADED mode."
            )

    def validate_plan(self, plan: dict) -> dict:
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
            "status": "READY" if self.kuzu and self.repo else "DEGRADED",
        }

    def dry_run(self, plan: dict) -> dict:
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
            "db_status": validation["status"],
        }

    def apply(self, plan: dict, allow_write: bool = True) -> dict:
        """
        Applies the plan. MANDATO: allow_write=True por defecto para habilitar mutación real.
        """
        if not allow_write:
            res = self.dry_run(plan)
            res["mode"] = (
                "dry_run_refused_write"  # Mantener compatibilidad con tests legacy
            )
            return res

        validation = self.validate_plan(plan)
        if not validation["valid"]:
            return {"status": "FAILED", "errors": validation["errors"]}

        if not self.kuzu or not self.repo:
            return {
                "status": "DEGRADED",
                "error": "Kuzu or Repository not initialized.",
                "writes_performed": False,
            }

        try:
            import json
            import re

            try:
                from layers.l2_brain.l2_memory_models import MemoryNode4D, IntentType
            except ImportError:
                from layers.l2_brain.l2_memory_models import MemoryNode4D, IntentType

            nodes_written = 0
            id_to_hash = {}

            for gnode in plan.get("nodes", []):
                node_id = gnode.get("node_id")
                parents = []
                for edge in plan.get("edges", []):
                    if edge.get("target") == node_id:
                        source_id = edge.get("source")
                        parent_hash = id_to_hash.get(source_id)
                        if parent_hash:
                            parents.append(parent_hash)
                        else:
                            source_node = next(
                                (
                                    n
                                    for n in plan.get("nodes", [])
                                    if n.get("node_id") == source_id
                                ),
                                None,
                            )
                            if (
                                source_node
                                and source_node.get("content_hash")
                                and re.match(
                                    r"^[a-f0-9]{64}$", source_node.get("content_hash")
                                )
                            ):
                                parents.append(source_node.get("content_hash"))
                            else:
                                parents.append(source_id)

                if not parents:
                    parents = ["GENESIS"]

                payload_dict = {
                    "node_id": node_id,
                    "node_type": gnode.get("node_type"),
                    "mission_id": gnode.get("mission_id"),
                    "properties": gnode.get("properties", {}),
                }
                payload = json.dumps(payload_dict)

                node = MemoryNode4D.from_intent_context(
                    parent_hashes=parents,
                    locus_x=gnode.get("mission_id") or "sovereign.mutation",
                    locus_y=gnode.get("phase_id") or "L2_BRAIN",
                    locus_z=gnode.get("node_type") or "SovereignNode",
                    lamport_t=0,
                    authority_a=AuthorityLevel.OVERSEER,
                    intent_i=IntentType.CRYSTALLIZATION,
                    payload=payload,
                )

                self.repo.create_memory_node(node)
                id_to_hash[node_id] = node.causal_hash
                nodes_written += 1

            return {
                "status": "SUCCESS",
                "mode": "sovereign_apply",
                "nodes_written": nodes_written,
                "db_status": "READY",
                "writes_performed": True,
                "simulation": False,
                "id_to_hash": id_to_hash,  # Requerido por tests
            }
        except Exception as e:
            logger.error(f"Sovereign write failed: {e}")
            return {"status": "FAILED", "error": str(e), "writes_performed": False}
