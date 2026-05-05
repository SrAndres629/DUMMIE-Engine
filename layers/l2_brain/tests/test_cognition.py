import sys
import os
from pathlib import Path

# Fix paths for test
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from cognition.epistemic_judge import EpistemicJudge
from cognition.cold_planner import ColdPlanner

def test_epistemic_judge():
    judge = EpistemicJudge()

    # Caso: Evidencia de test (peso 1.0)
    res = judge.evaluate_claim("El motor compila", [{"type": "test", "contradicts": False}])
    assert res["status"] == "SUPPORTED"
    assert res["confidence"] == 1.0

    # Caso: Contradicción
    res = judge.evaluate_claim("El motor compila", [{"type": "test", "contradicts": True}])
    assert res["status"] == "CONTRADICTED"

def test_cold_planner():
    planner = ColdPlanner()
    candidates = [
        {
            "id": "safe_fix",
            "rationale": "Small bugfix",
            "metrics": {"impact_on_mvp": 0.8, "risk_reduction": 0.9, "reversibility": 1.0}
        },
        {
            "id": "risky_refactor",
            "rationale": "Change everything",
            "metrics": {"impact_on_mvp": 0.5, "risk_reduction": 0.1, "reversibility": 0.1}
        }
    ]
    res = planner.select_next_action(candidates)
    assert res["selected_action"] == "safe_fix"
    print("Tests de cognición PASSED")

if __name__ == "__main__":
    test_epistemic_judge()
    test_cold_planner()
