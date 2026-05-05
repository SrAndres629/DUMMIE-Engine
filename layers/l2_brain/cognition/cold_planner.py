
import logging
from typing import Any, Dict, List

logger = logging.getLogger("dummie.brain.cognition.planner")

class ColdPlanner:
    """
    Planificador 'frío' que prioriza seguridad, impacto y reversibilidad.
    """

    PRIORITY_WEIGHTS = {
        "impact_on_mvp": 0.30,
        "risk_reduction": 0.20,
        "unblock_future_loops": 0.20,
        "testability": 0.15,
        "implementation_cost_inverse": 0.10,
        "reversibility": 0.05
    }

    RISK_PENALTIES = {
        "massive": 0.25,
        "refactor": 0.20,
        "destructive": 0.55,
    }

    def rank_actions(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        ranked = [self._score_candidate(candidate) for candidate in candidates]
        return sorted(ranked, key=lambda x: x["score"], reverse=True)

    def select_next_action(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        ranked = self.rank_actions(candidates)
        if not ranked:
            return {}

        selected = ranked[0]
        rejected_actions = ranked[1:]
        return {
            "selected_action": selected.get("id"),
            "score": selected.get("score"),
            "why": selected.get("rationale"),
            "rejected_actions": rejected_actions,
            "required_tests": selected.get("required_tests", []),
            "risk_level": selected.get("risk_level"),
            "patch_boundary": {
                "max_files": 5,
                "allowed_paths": selected.get("paths", []),
                "forbidden_paths": selected.get("forbidden_paths", []),
            },
        }

    def _score_candidate(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        metrics = candidate.get("metrics", {})
        base_score = sum(
            metrics.get(key, 0.5) * weight
            for key, weight in self.PRIORITY_WEIGHTS.items()
        )
        penalty = sum(
            metrics.get(key, 0.0) * weight
            for key, weight in self.RISK_PENALTIES.items()
        )
        penalty += metrics.get("risk", 0.0) * 0.25

        scored = dict(candidate)
        score = max(0.0, min(1.0, base_score - penalty))
        scored["score"] = round(score, 4)
        scored["risk_level"] = self._risk_level(scored, penalty)
        return scored

    @staticmethod
    def _risk_level(candidate: Dict[str, Any], penalty: float) -> str:
        metrics = candidate.get("metrics", {})
        if metrics.get("destructive", 0.0) > 0 or penalty >= 0.45:
            return "high"
        if metrics.get("massive", 0.0) > 0 or metrics.get("refactor", 0.0) > 0:
            return "high"
        if metrics.get("risk", 0.0) >= 0.4 or candidate["score"] < 0.6:
            return "medium"
        return "low"
