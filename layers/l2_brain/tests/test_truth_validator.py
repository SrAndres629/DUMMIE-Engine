from layers.l2_brain.governance.truth_validator import DummieTruthValidator


def test_truth_validator_basic_admit():
    metadata = {
        "passing_tests": True,
        "schema_validated": True,
        "has_evidence_refs": True,
    }
    # report_evidence base rank is 50.
    # Bonuses: passing_tests (+5), schema_validated (+3), has_evidence_refs (+3) = +11
    # Effective rank: 50 + 11 = 61
    verdict = DummieTruthValidator.evaluate_artifact(
        "report_evidence",
        metadata,
        content="This is safe content.",
    )
    assert verdict.admitted
    assert verdict.effective_rank == 61
    assert "passing_tests (+5)" in verdict.bonuses


def test_truth_validator_secrets_rejected():
    metadata = {
        "passing_tests": True,
    }
    content = "export API_KEY='sk-or-v1-abcdef1234567890'"
    verdict = DummieTruthValidator.evaluate_artifact(
        "report_evidence",
        metadata,
        content=content,
    )
    assert not verdict.admitted
    assert verdict.effective_rank == 0
    assert "secret_detected" in verdict.demotions


def test_truth_validator_deprecated_rejected():
    metadata = {
        "lifecycle_state": "deprecated",
    }
    verdict = DummieTruthValidator.evaluate_artifact(
        "active_specs",
        metadata,
        content="Some intent description.",
    )
    assert not verdict.admitted
    assert verdict.effective_rank == 0
    assert "lifecycle_deprecated" in verdict.demotions


def test_truth_validator_high_confidence_gate():
    metadata = {
        "high_confidence_context_required": True,
        "unknown_freshness": True,
    }
    # active_specs base rank is 90.
    # Penalties: unknown_freshness (-15).
    # Effective rank: 90 - 15 = 75. But unknown_freshness is True, which rejects it from high confidence.
    verdict = DummieTruthValidator.evaluate_artifact(
        "active_specs",
        metadata,
        content="Testing high confidence gate.",
    )
    assert not verdict.admitted
    assert verdict.effective_rank == 75
    assert "unknown_freshness (-15)" in verdict.demotions
