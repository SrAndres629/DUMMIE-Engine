from cognition.epistemic_judge import EpistemicJudge


def test_evaluate_claim_supports_with_high_authority_evidence():
    judge = EpistemicJudge()

    result = judge.evaluate_claim(
        "Planner selects reversible fixes",
        [
            {
                "id": "spec-1",
                "type": "active_spec",
                "supports": True,
                "summary": "Spec requests reversible fixes.",
            },
            {
                "id": "test-1",
                "type": "test",
                "supports": True,
                "summary": "Regression test proves reversible fix selection.",
            },
        ],
    )

    assert result["claim"] == "Planner selects reversible fixes"
    assert result["confidence"] == 1.0
    assert result["status"] == "SUPPORTED"
    assert result["decision"] == "trust"
    assert [item["id"] for item in result["supporting_evidence"]] == ["test-1", "spec-1"]
    assert result["contradicting_evidence"] == []
    assert result["required_next_check"] is None


def test_higher_authority_contradiction_beats_lower_support():
    judge = EpistemicJudge()

    result = judge.evaluate_claim(
        "Generated report is accurate",
        [
            {"id": "report-1", "type": "generated_report", "supports": True},
            {"id": "code-1", "type": "source_code", "contradicts": True},
        ],
    )

    assert result["confidence"] == 0.85
    assert result["status"] == "CONTRADICTED"
    assert result["decision"] == "reject"
    assert [item["id"] for item in result["contradicting_evidence"]] == ["code-1"]
    assert result["required_next_check"] is None


def test_insufficient_evidence_requires_source_verification():
    judge = EpistemicJudge()

    result = judge.evaluate_claim("The daemon writes memory safely", [])

    assert result == {
        "claim": "The daemon writes memory safely",
        "confidence": 0.0,
        "status": "INSUFFICIENT_EVIDENCE",
        "supporting_evidence": [],
        "contradicting_evidence": [],
        "required_next_check": "verify_source",
        "decision": "verify_source",
    }


def test_low_authority_support_remains_assumption_until_verified():
    judge = EpistemicJudge()

    result = judge.evaluate_claim(
        "A comment says this is done",
        [{"id": "comment-1", "type": "comment", "supports": True}],
    )

    assert result["confidence"] == 0.25
    assert result["status"] == "ASSUMPTION"
    assert result["decision"] == "verify_source"
    assert result["required_next_check"] == "source_code_or_test"


def test_contradicted_branch_returns_correct_status_and_confidence():
    """Regression: dead code bug L53 previously assigned SUPPORTED then overwrote with CONTRADICTED."""
    judge = EpistemicJudge()

    result = judge.evaluate_claim(
        "Spec claims watcher is active",
        [
            {"id": "spec-1", "type": "active_spec", "supports": True},
            {"id": "code-1", "type": "source_code", "contradicts": True},
        ],
    )

    assert result["status"] == "CONTRADICTED"
    assert result["confidence"] == 0.85
    assert result["decision"] == "reject"
    assert result["required_next_check"] is None
    assert len(result["contradicting_evidence"]) == 1
    assert result["contradicting_evidence"][0]["id"] == "code-1"


def test_compare_sources_ranks_test_above_comment():
    judge = EpistemicJudge()

    assert judge.compare_sources({"type": "test"}, {"type": "comment"}) == 1
    assert judge.compare_sources({"type": "comment"}, {"type": "test"}) == -1


def test_compare_sources_returns_zero_for_equal_types():
    judge = EpistemicJudge()

    assert judge.compare_sources({"type": "test"}, {"type": "test"}) == 0


def test_compare_sources_handles_unknown_types():
    judge = EpistemicJudge()

    # Unknown types get default weight 0.1, so they're equal to each other
    assert judge.compare_sources({"type": "unknown_x"}, {"type": "unknown_y"}) == 0
    # But lower than any known type
    assert judge.compare_sources({"type": "comment"}, {"type": "unknown"}) == 1
