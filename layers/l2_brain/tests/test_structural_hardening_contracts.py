# Spec Reference: 192_embedding_mesh_foundation
import pytest
from layers.l2_brain.structural_hardening.contracts import (
    StructuralClass,
    EvidenceType,
    Recommendation,
    RiskLevel,
    StructuralFinding,
    StructuralTriageReport
)


def test_enums_definition():
    assert StructuralClass.ACTIVE_RUNTIME == "ACTIVE_RUNTIME"
    assert EvidenceType.FILE_EXISTS == "FILE_EXISTS"
    assert Recommendation.KEEP_AND_TEST == "KEEP_AND_TEST"
    assert RiskLevel.CRITICAL == "CRITICAL"


def test_structural_finding_validation():
    finding = StructuralFinding(
        path="layers/l2_brain/model_router.py",
        current_class=StructuralClass.UNKNOWN,
        proposed_class=StructuralClass.ACTIVE_RUNTIME,
        risk=RiskLevel.LOW,
        recommendation=Recommendation.KEEP_AND_TEST,
        confidence=1.0,
        evidence_refs=["FILE_EXISTS: layers/l2_brain/model_router.py"],
        reasons=["File physically exists."],
        related_specs=["doc/specs/101_model_router.md"],
        related_tests=["layers/l2_brain/tests/test_model_router.py"],
        related_runtime=[],
        safe_to_change=True,
        requires_human_review=False
    )
    
    assert finding.path == "layers/l2_brain/model_router.py"
    assert finding.proposed_class == StructuralClass.ACTIVE_RUNTIME
    assert finding.risk == RiskLevel.LOW
    assert finding.safe_to_change is True


def test_triage_report_validation():
    finding = StructuralFinding(
        path="layers/l2_brain/model_router.py",
        current_class=StructuralClass.UNKNOWN,
        proposed_class=StructuralClass.ACTIVE_RUNTIME,
        risk=RiskLevel.LOW,
        recommendation=Recommendation.KEEP_AND_TEST,
        confidence=1.0,
        evidence_refs=["FILE_EXISTS: layers/l2_brain/model_router.py"],
        reasons=["File physically exists."],
        related_specs=[],
        related_tests=[],
        related_runtime=[],
        safe_to_change=True,
        requires_human_review=False
    )
    
    report = StructuralTriageReport(
        generated_at="2026-05-18T19:56:56Z",
        base_commit="894978ba00bc6324408fe01d30aa5a620c165dd4",
        pack_name="Structural Hardening Pack 2",
        pack_status="triage_completed",
        repo_health_status="FAIL",
        files_analyzed=1,
        findings=[finding],
        summary_counts={"ACTIVE_RUNTIME": 1},
        top_actions=[],
        limitations=["None"],
        next_recommended_phase="Structural Hardening Pack 2.1"
    )
    
    assert report.files_analyzed == 1
    assert len(report.findings) == 1
    assert report.repo_health_status == "FAIL"
