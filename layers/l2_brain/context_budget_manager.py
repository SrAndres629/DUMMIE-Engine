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


CRITICAL_KINDS = {
    "system",
    "mission",
    "phase",
    "authority",
    "next_action",
    "recovery",
    "evidence",
}


class ContextBudgetManager:
    def __init__(self, budgets: dict[str, int] | None = None):
        self.budgets = budgets or DEFAULT_BUDGETS

    def allocate_budget(self, model_tier: str) -> dict:
        limit = self.budgets.get(model_tier, self.budgets["local_fast"])
        return {
            "model_tier": model_tier,
            "total_budget": limit,
            "compression_threshold": int(0.8 * limit),
        }

    def should_compress(self, context_packet: dict, budget: dict) -> bool:
        total_estimated = sum(
            item.get("estimated_tokens", 0) for item in context_packet.get("items", [])
        )
        return total_estimated > budget.get("compression_threshold", 0)

    def enforce_budget(self, context_packet: dict, budget: dict, session_tokens: int = 0, daily_limit: int = 0) -> dict:
        limit = budget["total_budget"]
        items = list(context_packet.get("items", []))

        # Calculate total tokens
        total_tokens = sum(item.get("estimated_tokens", 0) for item in items)
        
        # High pressure detection (session vs daily budget)
        is_high_pressure = False
        if daily_limit > 0 and session_tokens > (daily_limit * 0.8):
            is_high_pressure = True
            limit = int(limit * 0.5) # Aggressive reduction
            logger.info(f"Budget high pressure detected ({session_tokens}/{daily_limit}). Reducing local limit to {limit}.")

        if total_tokens <= limit:
            return {
                "items": items,
                "dropped_refs": [],
                "kept_refs": [item.get("id") for item in items if item.get("id")],
                "compressed_refs": [],
                "budget_exceeded": False,
                "pressure": "high" if is_high_pressure else "low" if total_tokens < limit * 0.5 else "medium",
                "reason": "under_budget" if not is_high_pressure else "high_pressure_enforced",
            }

        # Rules:
        # 1. Critical items (by priority OR kind) are preserved.
        # 2. Others are dropped by priority (lowest first).

        def is_critical(item: dict) -> bool:
            return (
                item.get("priority") == "critical"
                or item.get("kind") in CRITICAL_KINDS
            )

        critical_items = [item for item in items if is_critical(item)]
        critical_total = sum(item.get("estimated_tokens", 0) for item in critical_items)

        if critical_total > limit:
            logger.warning(
                f"Critical context ({critical_total}) exceeds total budget ({limit})"
            )
            # We keep them anyway as per rules
            return {
                "items": critical_items,
                "dropped_refs": [
                    item.get("id") or item.get("ref", "unknown")
                    for item in items
                    if not is_critical(item)
                ],
                "kept_refs": [item.get("id") for item in critical_items if item.get("id")],
                "compressed_refs": [],
                "budget_exceeded": True,
                "pressure": "extreme",
                "reason": "critical_items_exceed_budget",
            }

        # Filter non-critical and sort by priority (highest to lowest to KEEP them)
        non_critical = [item for item in items if not is_critical(item)]
        sorted_non_critical = sorted(
            non_critical, key=lambda x: PRIORITY_MAP.get(x.get("priority", "medium"), 2)
        )

        final_kept = list(critical_items)
        current_tokens = critical_total
        dropped_refs = []
        compressed_refs = []

        for item in sorted_non_critical:
            tokens = item.get("estimated_tokens", 0)
            if current_tokens + tokens <= limit:
                final_kept.append(item)
                current_tokens += tokens
            else:
                # If it doesn't fit, we either drop it or mark as compressed if it has a ref
                ref = item.get("id") or item.get("ref")
                if ref and item.get("priority") in {"high", "medium"}:
                    compressed_refs.append(ref)
                else:
                    dropped_refs.append(ref or "unknown")

        return {
            "items": final_kept,
            "dropped_refs": dropped_refs,
            "kept_refs": [item.get("id") for item in final_kept if item.get("id")],
            "compressed_refs": compressed_refs,
            "budget_exceeded": False, # We met it by dropping/compressing
            "pressure": "high" if current_tokens > limit * 0.9 else "medium",
            "reason": "budget_enforced_via_dropping_and_compression_hints",
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
