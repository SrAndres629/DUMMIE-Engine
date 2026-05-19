from pathlib import Path

from layers.l2_brain.structural_hardening.contracts import (
    EvidenceType,
    Recommendation,
    RiskLevel,
    StructuralClass,
    StructuralFinding,
    StructuralTriageReport,
)
from layers.l2_brain.structural_hardening.bindings import BindingStatus, ContractBindingRegistry


def test_structural_contract_enums_present():
    assert StructuralClass.ACTIVE_RUNTIME.value == "ACTIVE_RUNTIME"
    assert StructuralClass.ORPHAN_TEST_CANDIDATE.value == "ORPHAN_TEST_CANDIDATE"
    assert EvidenceType.FILE_EXISTS.value == "FILE_EXISTS"
    assert Recommendation.FREEZE_UNTIL_REVIEW.value == "FREEZE_UNTIL_REVIEW"
    assert RiskLevel.CRITICAL.value == "CRITICAL"


def test_structural_finding_and_report_models():
    finding = StructuralFinding(
        path="layers/l2_brain/model_router.py",
        current_class=StructuralClass.UNKNOWN,
        proposed_class=StructuralClass.ACTIVE_RUNTIME,
        risk=RiskLevel.MEDIUM,
        recommendation=Recommendation.MAP_TO_TEST,
        confidence=0.91,
        evidence_refs=[EvidenceType.FILE_EXISTS.value],
        reasons=["runtime candidate"],
        related_specs=["doc/specs/189_model_router.md"],
        related_tests=["layers/l2_brain/tests/test_model_router.py"],
        related_runtime=[],
        safe_to_change=False,
        requires_human_review=True,
    )

    report = StructuralTriageReport(
        generated_at="2026-05-18T00:00:00Z",
        base_commit="abc",
        pack_name="Structural Hardening Pack 2 - Contract-First Triage",
        pack_status="PASS_WITH_WARNINGS",
        repo_health_status="FAIL",
        files_analyzed=1,
        findings=[finding],
        summary_counts={"by_class": {"ACTIVE_RUNTIME": 1}, "by_risk": {"MEDIUM": 1}, "by_recommendation": {"MAP_TO_TEST": 1}},
        top_actions=[finding],
        limitations=["deterministic"],
        next_recommended_phase="Pack 2.1",
    )

    assert report.findings[0].confidence == 0.91
    assert report.pack_status == "PASS_WITH_WARNINGS"
    assert report.repo_health_status == "FAIL"


def test_binding_validation_requires_real_evidence():
    registry = ContractBindingRegistry()
    binding, validation = registry.evaluate(
        "layers/l1_nervous/bootstrap.py",
        repo_root=Path.cwd(),
        evidence={"evidence_refs": ["FILE_EXISTS", "IMPORTABLE"]},
    )
    assert binding is not None
    assert validation is not None
    assert validation.effective_risk in {RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL}
    assert validation.resolved_status in {
        BindingStatus.BOUND_ACTIVE_RUNTIME,
        BindingStatus.NEEDS_MANUAL_OWNER,
        BindingStatus.DEFERRED_NO_SAFE_ACTION,
    }
