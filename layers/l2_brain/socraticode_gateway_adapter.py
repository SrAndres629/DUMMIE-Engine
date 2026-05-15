from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

class SocraticodeGatewayAdapter:
    """
    [L2_BRAIN] Adapter for semantic retrieval via Socraticode MCP.
    Falls back to VaultEmbeddingIndex if MCP is unavailable.
    """
    def __init__(self, mcp_gateway: Any = None, fallback_index: Any = None):
        self.mcp_gateway = mcp_gateway
        self.fallback_index = fallback_index

    async def semantic_search(self, query: str, top_k: int = 5, filters: dict | None = None) -> dict:
        """
        Executes a semantic search against the MCP or fallback index.
        """
        results = []
        status = "FAILED"
        fallback_used = False

        if self.mcp_gateway:
            try:
                # Mock integration for MCP tool call
                mcp_res = await self.mcp_gateway.call_tool("socraticode", "semantic_search", {"query": query, "top_k": top_k, "filters": filters or {}})
                if mcp_res and isinstance(mcp_res, dict) and "results" in mcp_res:
                    results = self._normalize_mcp_results(mcp_res["results"])
                    status = "READY"
            except Exception as e:
                logger.warning(f"Socraticode MCP search failed: {e}. Attempting fallback.")

        if status == "FAILED" and self.fallback_index:
            try:
                fallback_res = self.fallback_index.search_similar(query, top_k)
                results = self._normalize_fallback_results(fallback_res)
                status = "DEGRADED"
                fallback_used = True
            except Exception as e:
                logger.error(f"Fallback VaultEmbeddingIndex search failed: {e}")

        return {
            "status": status,
            "query": query,
            "results": results,
            "fallback_used": fallback_used
        }

    async def retrieve_context(self, query: str, budget: dict | None = None) -> dict:
        """
        Convenience wrapper around semantic search, potentially respecting budget.
        """
        # In a full implementation, this might fetch full texts or summaries based on budget.
        return await self.semantic_search(query)

    async def explain_retrieval(self, query: str, results: list[dict]) -> dict:
        """
        Asks the MCP to explain why these results are relevant to the query.
        """
        if not self.mcp_gateway:
            return {"status": "DEGRADED", "explanation": "Fallback active. Cannot generate dynamic explanation."}
        
        try:
             # Mock integration for MCP tool call
             mcp_res = await self.mcp_gateway.call_tool("socraticode", "explain_retrieval", {"query": query, "results": results})
             return {
                 "status": "READY",
                 "explanation": mcp_res.get("explanation", "No explanation provided.") if isinstance(mcp_res, dict) else str(mcp_res)
             }
        except Exception as e:
             logger.warning(f"Socraticode MCP explanation failed: {e}")
             return {"status": "DEGRADED", "explanation": "Failed to generate dynamic explanation."}

    def _normalize_mcp_results(self, raw_results: list[dict]) -> list[dict]:
        normalized = []
        for r in raw_results:
            normalized.append({
                "vault_id": r.get("vault_id") or r.get("id", ""),
                "score": float(r.get("score", 0.0)),
                "summary": r.get("summary", ""),
                "source": "mcp"
            })
        return normalized

    def _normalize_fallback_results(self, raw_results: list[dict]) -> list[dict]:
        normalized = []
        for r in raw_results:
            normalized.append({
                "vault_id": r.get("vault_id", ""),
                "score": float(r.get("score", 0.0)),
                "summary": r.get("summary", ""),
                "source": "fallback"
            })
        return normalized
