import json
import re
from typing import Any, List, Dict

class ReasoningLogic:
    """
    [DOMAIN] Lógica pura de ranking, filtrado y modelado de contexto.
    Sin dependencias de infraestructura.
    """
    @staticmethod
    def rank_candidates(goal: str, candidates: List[Dict[str, Any]], max_selected: int = 5) -> List[Dict[str, Any]]:
        ranked = []
        goal_tokens = ReasoningLogic._tokens(goal)
        for candidate in candidates:
            side_effect = str(candidate.get("side_effect_level") or "read").lower()
            score = float(candidate.get("score") or 0.0)
            
            text = " ".join(str(candidate.get(k, "")) for k in ("id", "target", "text", "description") if candidate.get(k))
            overlap = ReasoningLogic._lexical_overlap(goal_tokens, ReasoningLogic._tokens(text))
            
            penalty = ReasoningLogic._side_effect_penalty(side_effect)
            if side_effect in {"write", "external"} and overlap >= 0.25:
                penalty = min(penalty, 0.05)
            
            score += overlap * 0.5
            if side_effect == "write" and any(t in goal_tokens for t in ["persist", "lesson", "log"]):
                score += 0.15
            
            score -= penalty
            normalized = dict(candidate)
            normalized["score"] = round(max(0.0, min(1.0, score)), 4)
            normalized["risk"] = ReasoningLogic._risk_for_side_effect(side_effect)
            ranked.append(normalized)
        
        ranked.sort(key=lambda item: item.get("score", 0.0), reverse=True)
        return ranked[:max(1, max_selected)]

    @staticmethod
    def shape_context_packet(goal: str, ranked: List[Dict[str, Any]], token_budget: int = 4000, cloud_agent: str = "generic") -> Dict[str, Any]:
        selected = [str(item.get("id") or item.get("target")) for item in ranked if item.get("id") or item.get("target")]
        packet = {
            "task_brief": goal[:max(80, token_budget // 4)],
            "selected_tools": selected[:5],
            "execution_hint": f"Prepare {cloud_agent} with selected tools.",
            "estimated_tokens": len(goal) // 4,
        }
        return packet

    @staticmethod
    def _tokens(text: str) -> List[str]:
        return [t for t in re.findall(r"[a-zA-Z0-9_]+", text.lower()) if len(t) > 2]

    @staticmethod
    def _lexical_overlap(tokens_a: List[str], tokens_b: List[str]) -> float:
        set_a = set(tokens_a)
        set_b = set(tokens_b)
        if not set_a or not set_b: return 0.0
        return len(set_a & set_b) / len(set_a)

    @staticmethod
    def _side_effect_penalty(side_effect: str) -> float:
        return {"read": 0.0, "none": 0.0, "write": 0.15, "external": 0.2, "destructive": 0.4}.get(side_effect, 0.1)

    @staticmethod
    def _risk_for_side_effect(side_effect: str) -> str:
        if side_effect == "destructive": return "high"
        if side_effect in {"write", "external"}: return "medium"
        return "low"
