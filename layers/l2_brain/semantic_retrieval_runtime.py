from __future__ import annotations

import logging
from typing import Any
from layers.l2_brain.socraticode_gateway_adapter import SocraticodeGatewayAdapter

logger = logging.getLogger(__name__)

class SemanticRetrievalRuntime:
    """
    [L2_BRAIN] Orchestrates semantic retrieval for context injection.
    """
    def __init__(
        self,
        socraticode_adapter: SocraticodeGatewayAdapter,
        context_budget_manager: Any = None,
        memory_graph_runtime: Any = None
    ):
        self.adapter = socraticode_adapter
        self.budget_manager = context_budget_manager
        self.memory_graph = memory_graph_runtime

    async def retrieve_for_prompt(self, prompt: str, hook_packet: dict | None = None) -> dict:
        """
        Retrieves semantic context based on an incoming user prompt.
        """
        res = await self.adapter.semantic_search(prompt)
        return self.build_context_packet(res, prompt)

    async def retrieve_for_mission(self, mission_id: str, phase_id: str, query: str) -> dict:
        """
        Retrieves semantic context explicitly for a mission phase.
        """
        res = await self.adapter.semantic_search(f"Mission {mission_id} Phase {phase_id}: {query}")
        return self.build_context_packet(res, query)

    def build_context_packet(self, retrieval_result: dict, original_query: str) -> dict:
        """
        Constructs the standardized context packet.
        """
        vault_refs = []
        context_refs = []
        
        # Simple extraction of references from results
        for r in retrieval_result.get("results", []):
            vid = r.get("vault_id")
            if vid:
                vault_refs.append(vid)
                context_refs.append(f"vault:{vid}")

        # Stub logic for budget pressure mapping
        pressure = "NORMAL"
        if self.budget_manager:
            budget = self.budget_manager.check_budget()
            if budget.get("ratio", 0) > 0.8:
                pressure = "HIGH"
                # If pressure is high, we might truncate refs here
                vault_refs = vault_refs[:2]
                context_refs = context_refs[:2]

        return {
            "status": retrieval_result.get("status", "FAILED"),
            "query": original_query,
            "results": retrieval_result.get("results", []),
            "context_refs": context_refs,
            "vault_refs": vault_refs,
            "memory_refs": vault_refs, # Simplified mapping
            "graph_refs": [], # Stub
            "budget_pressure": pressure,
            "fallback_used": retrieval_result.get("fallback_used", False),
            "retrieval_reason": "explicit_query",
            "sensor_first_decision": "ALLOW" # Default for now
        }
