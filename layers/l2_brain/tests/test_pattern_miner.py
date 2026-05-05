from cognition.pattern_miner import PatternMiner


def test_mine_patterns_reports_repeated_failure_hotspot_with_rule():
    miner = PatternMiner()
    events = [
        {"id": "e1", "kind": "test_failure", "path": "layers/l2_brain/cognition/judge.py"},
        {"id": "e2", "kind": "test_failure", "path": "layers/l2_brain/cognition/judge.py"},
        {"id": "e3", "kind": "test_failure", "path": "layers/l2_brain/cognition/judge.py"},
        {"id": "e4", "kind": "success", "path": "layers/l2_brain/cognition/planner.py"},
    ]

    patterns = miner.mine_patterns(events)

    assert patterns == [
        {
            "pattern_id": "hotspot_layers_l2_brain_cognition_judge.py",
            "name": "Repeated event hotspot",
            "confidence": 0.75,
            "evidence_refs": ["e1", "e2", "e3"],
            "hypothesis": "layers/l2_brain/cognition/judge.py has repeated test_failure events.",
            "proposed_rule": "Require focused regression coverage before changing this path.",
            "recommended_action": "STRENGTHEN_TESTS",
        }
    ]


def test_mine_patterns_returns_empty_list_without_repetition():
    miner = PatternMiner()

    assert miner.mine_patterns([{"id": "e1", "kind": "success", "path": "a.py"}]) == []
