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


def test_mine_patterns_detects_contract_drift():
    miner = PatternMiner()
    events = [
        {"id": "spec-1", "path": "layers/l2_brain/daemon.py", "type": "active_spec", "supports": True},
        {"id": "code-1", "path": "layers/l2_brain/daemon.py", "type": "source_code", "contradicts": True},
    ]

    patterns = miner.mine_patterns(events)

    drift = [p for p in patterns if p["name"] == "Contract drift"]
    assert len(drift) == 1
    assert drift[0]["pattern_id"] == "drift_layers_l2_brain_daemon.py"
    assert drift[0]["recommended_action"] == "RECONCILE_CONTRACT"
    assert "spec-1" in drift[0]["evidence_refs"]
    assert "code-1" in drift[0]["evidence_refs"]
    assert "supported by active_spec" in drift[0]["hypothesis"]
    assert "contradicted by source_code" in drift[0]["hypothesis"]


def test_mine_patterns_no_drift_without_contradiction():
    miner = PatternMiner()
    events = [
        {"id": "s1", "path": "a.py", "type": "spec", "supports": True},
        {"id": "s2", "path": "a.py", "type": "code", "supports": True},
    ]

    patterns = miner.mine_patterns(events)

    assert all(p["name"] != "Contract drift" for p in patterns)
