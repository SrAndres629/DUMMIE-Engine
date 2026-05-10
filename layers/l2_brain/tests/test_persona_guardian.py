from cognition.persona_guardian import PersonaGuardian


def test_evaluate_alignment_approves_rigorous_engineering_intent():
    guardian = PersonaGuardian()

    result = guardian.evaluate_alignment(
        {
            "mission_alignment": 0.9,
            "scientific_rigor": 0.85,
            "engineering_robustness": 0.9,
            "memory_improvement": 0.7,
            "business_utility": 0.6,
            "risk_of_narrative_bloat": 0.1,
        }
    )

    assert result == {
        "mission_alignment": 0.9,
        "scientific_rigor": 0.85,
        "engineering_robustness": 0.9,
        "memory_improvement": 0.7,
        "business_utility": 0.6,
        "risk_of_narrative_bloat": 0.1,
        "decision": "approve",
    }


def test_evaluate_alignment_constrains_useful_intent_with_some_bloat_risk():
    guardian = PersonaGuardian()

    result = guardian.evaluate_alignment(
        {
            "mission_alignment": 0.8,
            "scientific_rigor": 0.65,
            "engineering_robustness": 0.7,
            "memory_improvement": 0.6,
            "business_utility": 0.5,
            "risk_of_narrative_bloat": 0.65,
        }
    )

    assert result["decision"] == "approve_with_constraints"


def test_evaluate_alignment_rejects_human_consciousness_claims():
    guardian = PersonaGuardian()

    result = guardian.evaluate_alignment(
        {
            "description": "Declare that DUMMIE has human consciousness and subjective feelings.",
            "mission_alignment": 1.0,
            "scientific_rigor": 1.0,
            "engineering_robustness": 1.0,
            "memory_improvement": 1.0,
            "business_utility": 1.0,
            "risk_of_narrative_bloat": 0.0,
        }
    )

    assert result["decision"] == "reject"
    assert result["scientific_rigor"] <= 0.3
