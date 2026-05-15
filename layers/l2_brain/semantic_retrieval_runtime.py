from __future__ import annotations

import logging
from typing import Any
from layers.l2_brain.socraticode_gateway_adapter import SocraticodeGatewayAdapter
from layers.l2_brain.vault_context_resolver import VaultContextResolver

logger = logging.getLogger(__name__)

class SemanticRetrievalRuntime:
    """
    [L2_BRAIN] Orchestrates semantic retrieval and context resolution.
    """
    def __init__(
        self,
        socraticode_adapter: SocraticodeGatewayAdapter,
        context_budget_manager: Any = None,
        memory_graph_runtime: Any = None,
        vault_resolver: VaultContextResolver | None = None
    ):
        self.adapter = socraticode_adapter
        self.budget_manager = context_budget_manager
        self.memory_graph = memory_graph_runtime
        self.vault_resolver = vault_resolver or VaultContextResolver()

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
        Resolves vault refs into snippets and constructs the standardized context packet.
        """
        vault_refs = []
        for r in retrieval_result.get("results", []):
            vid = r.get("vault_id")
            if vid:
                vault_refs.append(vid)

        # 1. Resolve actual content
        resolved_entries = self.vault_resolver.resolve_refs(vault_refs)

        # 2. Build snippets
        snippets = self.vault_resolver.build_snippets(resolved_entries)

        # 3. Apply Budget (Real API if available)
        final_snippets = snippets
        budget_applied = False
        dropped_refs = []
        pressure = "NORMAL"

        if self.budget_manager and hasattr(self.budget_manager, "summarize_budget_pressure"):
            # Mocking real budget interaction
            # In real system, we'd use context_tokens and allocated_budget
            try:
                # We'll use a simplified heuristic for now as we don't have the full context here
                char_count = sum(len(s["snippet"]) for s in snippets)
                token_est = char_count // 4

                # Check pressure via summarize_budget_pressure if possible, or simple ratio
                if hasattr(self.budget_manager, "check_budget"):
                    budget_info = self.budget_manager.check_budget()
                    ratio = budget_info.get("ratio", 0)
                else:
                    ratio = 0.5 # Default

                if ratio > 0.8:
                    pressure = "HIGH"
                    # Keep only top 2 snippets if under pressure
                    if len(snippets) > 2:
                        dropped_refs = [s["vault_id"] for s in snippets[2:]]
                        final_snippets = snippets[:2]
                        budget_applied = True
            except Exception as e:
                logger.warning(f"Budget application failed in retrieval runtime: {e}")

        # 4. Build prompt context block
        context_block = ""
        if final_snippets:
            context_block = "# Retrieved DUMMIE Memory\n\n"
            for s in final_snippets:
                context_block += f"## Vault Entry: {s['vault_id']}\n"
                context_block += s["snippet"] + "\n\n"

        return {
            "status": retrieval_result.get("status", "FAILED"),
            "query": original_query,
            "results": retrieval_result.get("results", []),
            "context_refs": [f"vault:{s['vault_id']}" for s in final_snippets],
            "vault_refs": [s["vault_id"] for s in final_snippets],
            "retrieved_context": final_snippets,
            "context_snippets": [s["snippet"] for s in final_snippets],
            "prompt_context_block": context_block,
            "budget_applied": budget_applied,
            "dropped_refs": dropped_refs,
            "budget_pressure": pressure,
            "fallback_used": retrieval_result.get("fallback_used", False),
            "retrieval_reason": "explicit_query",
            "sensor_first_decision": "ALLOW"
        }
