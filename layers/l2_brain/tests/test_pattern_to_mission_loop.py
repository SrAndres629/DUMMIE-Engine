"""End-to-end test for the Pattern-to-Mission loop (OpenClaw loop).

Proves that:
  events → PatternMiner → PersonaGuardian → ColdPlanner 
  → PromptToMissionCompiler → new mission proposal
"""

from cognition.pattern_miner import PatternMiner
from cognition.persona_guardian import PersonaGuardian
from cognition.cold_planner import ColdPlanner
from prompt_to_mission import PromptToMissionCompiler


def test_pattern_to_mission_loop():
    # 1. Historical events show contract drift on test_flight.py
    events = [
        {"id": "spec-1", "path": "test_flight.py", "type": "active_spec", "supports": True},
        {"id": "code-1", "path": "test_flight.py", "type": "source_code", "contradicts": True},
    ]

    # 2. PatternMiner detects the drift
    miner = PatternMiner()
    patterns = miner.mine_patterns(events)
    drift_patterns = [p for p in patterns if p["name"] == "Contract drift"]
    assert len(drift_patterns) == 1
    target_pattern = drift_patterns[0]

    # 3. PersonaGuardian validates alignment of fixing this drift
    guardian = PersonaGuardian()
    alignment = guardian.evaluate_alignment({
        "metrics": {
            "scientific_rigor": 0.8,
            "engineering_robustness": 0.9,
            "risk_of_bloat": 0.1
        }
    })
    assert alignment["decision"] == "approve"

    # 4. ColdPlanner prefers fixing the contract drift over a massive refactor
    planner = ColdPlanner()
    candidates = [
        {
            "id": "fix_contract_drift",
            "rationale": "Reconcile spec and code.",
            "metrics": {
                "impact_on_mvp": 0.8,
                "risk_reduction": 0.9,
                "testability": 0.9,
                "reversibility": 1.0,
            },
        },
        {
            "id": "massive_refactor",
            "rationale": "Rewrite everything.",
            "metrics": {
                "impact_on_mvp": 1.0,
                "destructive": 1.0,
            },
        },
    ]
    selected = planner.select_next_action(candidates)
    assert selected["selected_action"] == "fix_contract_drift"

    # 5. PromptToMissionCompiler generates a new system mission from the pattern
    compiler = PromptToMissionCompiler()
    mission = compiler.compile_from_pattern(
        target_pattern,
        context={"evidence_refs": target_pattern["evidence_refs"]}
    )

    # 6. Verify the new mission
    assert mission["authority_a"] == "SYSTEM"
    assert mission["source_pattern_id"] == "drift_test_flight.py"
    assert "Contract drift" in mission["goal"]
    assert "RECONCILE_CONTRACT" in mission["goal"]
    assert "test_flight.py has contradicting evidence" in mission["goal"]
    assert mission["context_refs"] == ["spec-1", "code-1"]
    
    # It must have the mandatory phases
    assert "EPISTEMIC_CHECK" in mission["phases"]
    assert "NEXT_LOOP" in mission["phases"]
