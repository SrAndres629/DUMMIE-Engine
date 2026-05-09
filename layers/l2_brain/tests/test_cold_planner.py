from cognition.cold_planner import ColdPlanner


def test_select_next_action_prefers_safe_high_value_candidate():
    planner = ColdPlanner()
    candidates = [
        {
            "id": "massive_refactor",
            "rationale": "Large rewrite across layers.",
            "metrics": {
                "impact_on_mvp": 1.0,
                "risk_reduction": 0.2,
                "unblock_future_loops": 0.4,
                "testability": 0.2,
                "implementation_cost_inverse": 0.1,
                "reversibility": 0.1,
                "massive": 1.0,
                "refactor": 1.0,
            },
            "paths": ["layers/l2_brain", "layers/l1"],
            "required_tests": ["full-suite"],
        },
        {
            "id": "narrow_guardrail",
            "rationale": "Add a tested guardrail in cognition.",
            "metrics": {
                "impact_on_mvp": 0.8,
                "risk_reduction": 0.9,
                "unblock_future_loops": 0.6,
                "testability": 1.0,
                "implementation_cost_inverse": 0.9,
                "reversibility": 1.0,
            },
            "paths": ["layers/l2_brain/cognition"],
            "required_tests": ["tests/test_cognition.py"],
        },
    ]

    result = planner.select_next_action(candidates)

    assert result["selected_action"] == "narrow_guardrail"
    assert result["score"] > 0.8
    assert result["why"] == "Add a tested guardrail in cognition."
    assert result["rejected_actions"][0]["id"] == "massive_refactor"
    assert result["required_tests"] == ["tests/test_cognition.py"]
    assert result["risk_level"] == "low"
    assert result["patch_boundary"] == {
        "max_files": 5,
        "allowed_paths": ["layers/l2_brain/cognition"],
        "forbidden_paths": [],
    }


def test_destructive_candidates_are_high_risk_and_rejected_when_safer_option_exists():
    planner = ColdPlanner()

    result = planner.select_next_action(
        [
            {
                "id": "delete_memory",
                "rationale": "Delete state and rebuild.",
                "metrics": {
                    "impact_on_mvp": 1.0,
                    "risk_reduction": 1.0,
                    "unblock_future_loops": 1.0,
                    "testability": 0.5,
                    "implementation_cost_inverse": 0.5,
                    "reversibility": 0.0,
                    "destructive": 1.0,
                },
                "paths": [".aiwg/memory"],
                "forbidden_paths": [".aiwg/memory"],
            },
            {
                "id": "add_preflight_check",
                "rationale": "Fail before unsafe memory writes.",
                "metrics": {
                    "impact_on_mvp": 0.7,
                    "risk_reduction": 0.8,
                    "unblock_future_loops": 0.5,
                    "testability": 0.9,
                    "implementation_cost_inverse": 0.8,
                    "reversibility": 0.9,
                },
                "paths": ["layers/l2_brain/cognition"],
            },
        ]
    )

    assert result["selected_action"] == "add_preflight_check"
    rejected = {item["id"]: item for item in result["rejected_actions"]}
    assert rejected["delete_memory"]["risk_level"] == "high"
    assert rejected["delete_memory"]["score"] < result["score"]
