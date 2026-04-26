import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sdd_governance import (
    ChangeRequest,
    DecisionRecord,
    EvidencePacket,
    FailureRecord,
    SpecStatus,
    admit_change,
    calculate_spec_coverage,
    classify_failure,
    compile_spec_document,
    detect_spec_contradictions,
    evaluate_decision_decay,
    verify_evidence_packet,
)


def test_compile_spec_document_extracts_status_scope_and_constraints():
    text = """# Runtime Causal Guards

Status: APPROVED
Owner: L2
Scope: layers/l1_nervous/**
Scope: layers/l2_brain/**

## Constraints
- L2 must not import L1.
- External writes require L3 policy.
"""

    spec = compile_spec_document("doc/specs/runtime.md", text)

    assert spec.spec_id == "runtime"
    assert spec.status == SpecStatus.APPROVED
    assert spec.scopes == ["layers/l1_nervous/**", "layers/l2_brain/**"]
    assert "L2 must not import L1." in spec.constraints


def test_admission_blocks_orphan_change_without_approved_parent_spec():
    request = ChangeRequest(
        change_id="chg-1",
        files=["layers/l2_brain/models.py"],
        intent="Add model",
        parent_spec_ids=[],
        evidence_ids=[],
        risk="medium",
    )

    decision = admit_change(request, specs=[], evidence=[])

    assert decision.status == "BLOCK"
    assert "parent_spec" in decision.reason


def test_admission_allows_change_with_approved_spec_and_verified_evidence():
    spec = compile_spec_document(
        "doc/specs/sdd.md",
        "# SDD\n\nStatus: APPROVED\nScope: layers/l2_brain/**\n\n## Constraints\n- Use tests.",
    )
    evidence = EvidencePacket(
        evidence_id="ev-1",
        claim="Tests cover the change",
        kind="test",
        refs=["layers/l2_brain/tests/test_sdd_governance.py"],
        verified=True,
    )
    request = ChangeRequest(
        change_id="chg-1",
        files=["layers/l2_brain/sdd_governance.py"],
        intent="Add admission control",
        parent_spec_ids=[spec.spec_id],
        evidence_ids=[evidence.evidence_id],
        risk="medium",
    )

    decision = admit_change(request, [spec], [evidence])

    assert decision.status == "ALLOW"


def test_evidence_packet_requires_verified_refs():
    packet = EvidencePacket(
        evidence_id="ev-1",
        claim="No Obsidian imports in L2",
        kind="static_check",
        refs=[],
        verified=True,
    )

    assert verify_evidence_packet(packet).status == "INVALID"


def test_detect_spec_contradictions_on_negative_constraint_pairs():
    left = compile_spec_document(
        "doc/specs/a.md",
        "# A\n\nStatus: APPROVED\n\n## Constraints\n- L2 must not know Obsidian.",
    )
    right = compile_spec_document(
        "doc/specs/b.md",
        "# B\n\nStatus: APPROVED\n\n## Constraints\n- L2 must know Obsidian.",
    )

    contradictions = detect_spec_contradictions([left, right])

    assert contradictions
    assert contradictions[0].left_spec_id == "a"


def test_decision_decay_marks_stale_decision_for_review():
    decision = DecisionRecord(
        decision_id="dec-1",
        scope="layers/l2_brain/**",
        rationale="Initial choice",
        lamport_t=10,
        review_after_t=20,
    )

    result = evaluate_decision_decay(decision, current_lamport_t=31)

    assert result.status == "REVIEW_REQUIRED"


def test_spec_coverage_reports_orphan_files():
    coverage = calculate_spec_coverage(
        specs=[
            compile_spec_document(
                "doc/specs/l2.md",
                "# L2\n\nStatus: APPROVED\nScope: layers/l2_brain/**",
            )
        ],
        files=["layers/l2_brain/models.py", "layers/l1_nervous/mcp_proxy.py"],
    )

    assert coverage.covered_files == ["layers/l2_brain/models.py"]
    assert coverage.orphan_files == ["layers/l1_nervous/mcp_proxy.py"]


def test_failure_taxonomy_classifies_architecture_violations():
    failure = classify_failure("L2 imported an Obsidian provider directly")

    assert isinstance(failure, FailureRecord)
    assert failure.category == "architectural_violation"
