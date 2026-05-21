from __future__ import annotations

import logging
import json
from typing import Any

logger = logging.getLogger(__name__)

class SocraticodeGatewayAdapter:
    """
    [L2_BRAIN] Adapter for semantic retrieval via Socraticode MCP.
    Supports call_tool and execute_tool with fallback to VaultEmbeddingIndex.
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
        method_used = "none"

        # Try call_tool
        if self.mcp_gateway and hasattr(self.mcp_gateway, "call_tool"):
            try:
                mcp_res = await self.mcp_gateway.call_tool(
                    "socraticode",
                    "semantic_search",
                    {"query": query, "top_k": top_k, "filters": filters or {}}
                )
                if self._is_valid_mcp_res(mcp_res):
                    results = self._normalize_mcp_results(mcp_res["results"])
                    status = "READY"
                    method_used = "call_tool"
            except Exception as e:
                logger.debug(f"Socraticode MCP call_tool failed: {e}")

        # Try execute_tool if call_tool failed
        if status == "FAILED" and self.mcp_gateway and hasattr(self.mcp_gateway, "execute_tool"):
            try:
                mcp_res = await self.mcp_gateway.execute_tool(
                    "socraticode",
                    "semantic_search",
                    {"query": query, "top_k": top_k, "filters": filters or {}}
                )
                if self._is_valid_mcp_res(mcp_res):
                    results = self._normalize_mcp_results(mcp_res["results"])
                    status = "READY"
                    method_used = "execute_tool"
            except Exception as e:
                logger.debug(f"Socraticode MCP execute_tool failed: {e}")

        # Fallback to local index
        if status == "FAILED" and self.fallback_index:
            try:
                fallback_res = self.fallback_index.search_similar(query, top_k)
                results = self._normalize_fallback_results(fallback_res)
                status = "DEGRADED"
                fallback_used = True
                method_used = "fallback_index"
            except Exception as e:
                logger.error(f"Fallback VaultEmbeddingIndex search failed: {e}")

        return {
            "status": status,
            "query": query,
            "results": results,
            "fallback_used": fallback_used,
            "adapter_method_used": method_used
        }

    async def retrieve_context(self, query: str, budget: dict | None = None) -> dict:
        return await self.semantic_search(query)

    async def explain_retrieval(self, query: str, results: list[dict]) -> dict:
        if not self.mcp_gateway:
            return {"status": "DEGRADED", "explanation": "Fallback active. Cannot generate dynamic explanation."}

        args = {"query": query, "results": results}

        # Try call_tool
        if hasattr(self.mcp_gateway, "call_tool"):
            try:
                mcp_res = await self.mcp_gateway.call_tool("socraticode", "explain_retrieval", args)
                return {"status": "READY", "explanation": self._extract_explanation(mcp_res)}
            except Exception: pass

        # Try execute_tool
        if hasattr(self.mcp_gateway, "execute_tool"):
            try:
                mcp_res = await self.mcp_gateway.execute_tool("socraticode", "explain_retrieval", args)
                return {"status": "READY", "explanation": self._extract_explanation(mcp_res)}
            except Exception: pass

        return {"status": "DEGRADED", "explanation": "Failed to generate dynamic explanation."}

    def _is_valid_mcp_res(self, res: Any) -> bool:
        if not isinstance(res, dict): return False
        if "results" in res: return True
        # Handle cases where result is wrapped in 'result' key
        if "result" in res and isinstance(res["result"], dict) and "results" in res["result"]:
            return True
        return False

    def _normalize_mcp_results(self, raw_results: Any) -> list[dict]:
        # Handle wrapping if needed
        if isinstance(raw_results, dict) and "results" in raw_results:
            raw_results = raw_results["results"]

        if not isinstance(raw_results, list): return []

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

    def _extract_explanation(self, res: Any) -> str:
        if isinstance(res, dict):
            if "explanation" in res: return str(res["explanation"])
            if "result" in res and isinstance(res["result"], dict):
                return str(res["result"].get("explanation", "No explanation provided."))
        return str(res)
