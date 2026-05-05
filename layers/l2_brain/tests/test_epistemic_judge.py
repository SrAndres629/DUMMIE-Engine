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
