from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_BUDGETS = {
    "deterministic": 2048,
    "local_fast": 4096,
    "local_deep": 16384,
    "cloud_std": 32768,
    "cloud_prem": 128000,
}

PRIORITY_MAP = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


class ContextBudgetManager:
    def __init__(self, budgets: dict[str, int] | None = None):
        self.budgets = budgets or DEFAULT_BUDGETS

    def allocate_budget(self, model_tier: str) -> dict:
        limit = self.budgets.get(model_tier, self.budgets["local_fast"])
        return {
            "model_tier": model_tier,
            "total_budget": limit,
            "compression_threshold": 0.8 * limit,
        }

    def should_compress(self, context_packet: dict, budget: dict) -> bool:
        total_estimated = sum(item.get("estimated_tokens", 0) for item in context_packet.get("items", []))
        return total_estimated > budget.get("compression_threshold", 0)

    def enforce_budget(self, context_packet: dict, budget: dict) -> dict:
        limit = budget["total_budget"]
        items = list(context_packet.get("items", []))
        
        # Calculate total tokens
        total_tokens = sum(item.get("estimated_tokens", 0) for item in items)
        
        if total_tokens <= limit:
            return {
                "items": items,
                "dropped_refs": [],
                "kept_refs": [item.get("id") for item in items if item.get("id")],
                "budget_exceeded": False,
                "pressure": "low" if total_tokens < limit * 0.5 else "medium",
            }

        # Need to drop items. Sort by priority (descending, so low priority first)
        # and then by age (placeholder: assuming items are in chronological order, 
        # so we drop older ones of same priority first)
        
        # Stability: items with same priority should be handled in a way that preserves newer ones?
        # Let's sort: priority 3 (low) first, priority 0 (critical) last.
        sorted_items = sorted(items, key=lambda x: PRIORITY_MAP.get(x.get("priority", "medium"), 2), reverse=True)
        
        kept_items = []
        dropped_refs = []
        current_total = 0
        
        # We must keep CRITICAL items even if they exceed the budget? 
        # Requirement says "preserve always critical".
        
        critical_items = [item for item in items if item.get("priority") == "critical"]
        critical_total = sum(item.get("estimated_tokens", 0) for item in critical_items)
        
        if critical_total > limit:
            logger.warning(f"Critical context ({critical_total}) exceeds total budget ({limit})")
            # We keep them anyway as per rules
            return {
                "items": critical_items,
                "dropped_refs": [item.get("id") for item in items if item.get("priority") != "critical"],
                "kept_refs": [item.get("id") for item in critical_items],
                "budget_exceeded": True,
                "pressure": "extreme",
            }

        # Filter out critical items for the greedy selection
        non_critical = [item for item in items if item.get("priority") != "critical"]
        # Sort non_critical by priority (lower priority first to be considered for DROPPING)
        # Wait, if we want to KEEP high priority, we should sort by priority (ASCENDING: 0, 1, 2, 3) 
        # and take until limit.
        
        sorted_for_keeping = sorted(items, key=lambda x: PRIORITY_MAP.get(x.get("priority", "medium"), 2))
        
        final_kept = []
        current_tokens = 0
        for item in sorted_for_keeping:
            tokens = item.get("estimated_tokens", 0)
            if item.get("priority") == "critical" or current_tokens + tokens <= limit:
                final_kept.append(item)
                current_tokens += tokens
            else:
                dropped_refs.append(item.get("id") or item.get("ref", "unknown"))

        return {
            "items": final_kept,
            "dropped_refs": dropped_refs,
            "kept_refs": [item.get("id") for item in final_kept if item.get("id")],
            "budget_exceeded": current_tokens > limit,
            "pressure": "high" if current_tokens > limit * 0.9 else "medium",
        }

    def summarize_budget_pressure(self, context_packet: dict, budget: dict) -> dict:
        total_tokens = sum(item.get("estimated_tokens", 0) for item in context_packet.get("items", []))
        limit = budget["total_budget"]
        ratio = total_tokens / limit if limit > 0 else 1.0
        
        pressure = "low"
        if ratio > 1.0: pressure = "extreme"
        elif ratio > 0.9: pressure = "high"
        elif ratio > 0.7: pressure = "medium"
        
        return {
            "total_tokens": total_tokens,
            "limit": limit,
            "ratio": ratio,
            "pressure": pressure,
        }
