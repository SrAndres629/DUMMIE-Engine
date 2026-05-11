from typing import Dict, Any, List, Optional

class ContextBudgetManager:
    """
    [L2_BRAIN] Manages context allocation and enforces token budgets.
    """
    def __init__(self, default_max_tokens: int = 32000):
        self.default_max_tokens = default_max_tokens
        self.budgets: Dict[str, Dict[str, Any]] = {}

    def allocate_budget(self, session_id: str, mission_id: Optional[str] = None, max_tokens: Optional[int] = None, priority: int = 1) -> Dict[str, Any]:
        budget_id = mission_id or session_id
        budget = {
            "session_id": session_id,
            "mission_id": mission_id,
            "max_tokens": max_tokens or self.default_max_tokens,
            "consumed_tokens": 0,
            "priority": priority,
            "enforcement_policy": "soft" if priority > 5 else "hard"
        }
        self.budgets[budget_id] = budget
        return budget

    def update_usage(self, budget_id: str, tokens: int):
        if budget_id in self.budgets:
            self.budgets[budget_id]["consumed_tokens"] += tokens

    def should_compress(self, budget_id: str, current_request_tokens: int) -> bool:
        if budget_id not in self.budgets:
            return False
            
        budget = self.budgets[budget_id]
        total_potential = budget["consumed_tokens"] + current_request_tokens
        usage_ratio = total_potential / budget["max_tokens"]
        
        return usage_ratio > 0.8

    def enforce_budget(self, budget_id: str, context_packet: List[Dict[str, Any]], current_tokens: int) -> Dict[str, Any]:
        """
        Returns a decision and potentially a truncated/compressed context list.
        """
        if budget_id not in self.budgets:
            return {"action": "allow", "context": context_packet}
            
        budget = self.budgets[budget_id]
        if not self.should_compress(budget_id, current_tokens):
            return {"action": "allow", "context": context_packet}
            
        # Basic heuristic: if hard/strict and over limit, truncate oldest
        if budget["enforcement_policy"] == "hard" and (budget["consumed_tokens"] + current_tokens) > budget["max_tokens"]:
            # Truncate logic would go here
            return {"action": "compress_required", "context": context_packet, "reason": "budget_pressure"}
            
        return {"action": "warn", "context": context_packet, "reason": "approaching_limit"}

    def summarize_budget_pressure(self, session_id: str) -> Dict[str, Any]:
        session_budgets = [b for b in self.budgets.values() if b["session_id"] == session_id]
        if not session_budgets:
            return {"status": "nominal", "pressure": 0.0}
            
        avg_pressure = sum(b["consumed_tokens"] / b["max_tokens"] for b in session_budgets) / len(session_budgets)
        
        return {
            "status": "critical" if avg_pressure > 0.9 else "high" if avg_pressure > 0.7 else "nominal",
            "avg_pressure": round(avg_pressure, 4),
            "active_budgets": len(session_budgets)
        }
