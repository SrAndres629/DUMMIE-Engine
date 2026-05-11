import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

class TokenCostLedger:
    """
    [L2_BRAIN] Centralized ledger for tracking token costs across sessions and missions.
    """
    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def record_usage(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Records a token usage event.
        """
        event_id = event.get("event_id") or uuid.uuid4().hex[:12]
        timestamp = event.get("timestamp") or datetime.now().isoformat()
        
        full_event = {
            "event_id": event_id,
            "timestamp": timestamp,
            "session_id": event.get("session_id", "unknown"),
            "mission_id": event.get("mission_id", "unknown"),
            "model_tier": event.get("model_tier", "deterministic"),
            "provider": event.get("provider", "unknown"),
            "input_tokens": int(event.get("input_tokens", 0)),
            "cached_tokens": int(event.get("cached_tokens", 0)),
            "output_tokens": int(event.get("output_tokens", 0)),
            "reasoning_tokens": int(event.get("reasoning_tokens", 0)),
            "estimated": bool(event.get("estimated", True)),
            "source": event.get("source", "manual")
        }
        
        self.events.append(full_event)
        return full_event

    def summarize_session(self, session_id: str) -> Dict[str, Any]:
        session_events = [e for e in self.events if e["session_id"] == session_id]
        return self._summarize_events(session_events)

    def summarize_mission(self, mission_id: str) -> Dict[str, Any]:
        mission_events = [e for e in self.events if e["mission_id"] == mission_id]
        return self._summarize_events(mission_events)

    def _summarize_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        summary = {
            "total_input": sum(e["input_tokens"] for e in events),
            "total_output": sum(e["output_tokens"] for e in events),
            "total_cached": sum(e["cached_tokens"] for e in events),
            "total_reasoning": sum(e["reasoning_tokens"] for e in events),
            "event_count": len(events),
            "tiers": {}
        }
        
        for e in events:
            tier = e["model_tier"]
            if tier not in summary["tiers"]:
                summary["tiers"][tier] = {"input": 0, "output": 0}
            summary["tiers"][tier]["input"] += e["input_tokens"]
            summary["tiers"][tier]["output"] += e["output_tokens"]
            
        return summary

    def cache_hit_ratio(self, session_id: str) -> float:
        summary = self.summarize_session(session_id)
        total_input = summary["total_input"] + summary["total_cached"]
        if total_input == 0:
            return 0.0
        return round(summary["total_cached"] / total_input, 4)

    def cloud_cost_estimate(self, session_id: str) -> Dict[str, Any]:
        # Heuristic costs in USD per 1M tokens
        PRICES = {
            "cloud_std": {"input": 3.0, "output": 15.0},
            "cloud_prem": {"input": 15.0, "output": 60.0},
            "local_fast": {"input": 0.0, "output": 0.0},
            "local_deep": {"input": 0.0, "output": 0.0},
            "deterministic": {"input": 0.0, "output": 0.0}
        }
        
        summary = self.summarize_session(session_id)
        total_cost = 0.0
        
        for tier, counts in summary["tiers"].items():
            price = PRICES.get(tier, {"input": 0, "output": 0})
            total_cost += (counts["input"] / 1_000_000) * price["input"]
            total_cost += (counts["output"] / 1_000_000) * price["output"]
            
        return {
            "currency": "USD",
            "estimated_total": round(total_cost, 6)
        }
