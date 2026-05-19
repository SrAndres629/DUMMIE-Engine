from layers.l2_brain.structural_hardening.classifier import StructuralClassifier
from layers.l2_brain.structural_hardening.contracts import Recommendation, RiskLevel, StructuralClass


def _ev(**kwargs):
    base = {
        "evidence_refs": ["FILE_EXISTS"],
        "reasons": [],
        "related_specs": [],
        "related_tests": [],
        "related_runtime": [],
    }
    base.update(kwargs)
    return base


def test_init_py_not_shadow_high_risk():
    c = StructuralClassifier()
    rec = {"path": "layers/l2_brain/__init__.py", "classification": "UNKNOWN"}
    finding = c.classify(rec, _ev())
    assert finding.proposed_class == StructuralClass.ACTIVE_RUNTIME
    assert finding.risk == RiskLevel.LOW


def test_spec_and_test_and_generated_and_legacy_and_config_and_report_rules():
    c = StructuralClassifier()

    spec = c.classify({"path": "doc/specs/190_demo.md", "classification": "SPEC"}, _ev(related_runtime=["layers/l2_brain/model_router.py"]))
    assert spec.proposed_class == StructuralClass.ACTIVE_SPEC

    test = c.classify(
        {"path": "layers/l2_brain/tests/test_model_router.py", "classification": "TEST"},
        _ev(related_runtime=["layers/l2_brain/model_router.py"]),
    )
    assert test.proposed_class == StructuralClass.ACTIVE_TEST

    orphan = c.classify({"path": "tests/test_orphan.py", "classification": "TEST"}, _ev())
    assert orphan.proposed_class == StructuralClass.ORPHAN_TEST_CANDIDATE
    assert orphan.recommendation == Recommendation.MAP_TO_RUNTIME

    generated = c.classify({"path": "layers/l2_brain/proto/x_pb2.py", "classification": "GENERATED"}, _ev())
    assert generated.proposed_class == StructuralClass.GENERATED

    legacy = c.classify({"path": "doc/.deprecated/old.py", "classification": "LEGACY"}, _ev())
    assert legacy.proposed_class == StructuralClass.LEGACY

    config = c.classify({"path": "pyproject.toml", "classification": "CONFIG"}, _ev())
    assert config.proposed_class == StructuralClass.CONFIG

    report = c.classify({"path": ".aiwg/reports/semantic_repo_index_latest.json", "classification": "REPORT"}, _ev())
    assert report.proposed_class == StructuralClass.REPORT


def test_runtime_not_unknown():
    c = StructuralClassifier()
    runtime = c.classify(
        {"path": "layers/l2_brain/model_router.py", "classification": "ACTIVE_RUNTIME"},
        _ev(related_tests=["layers/l2_brain/tests/test_model_router.py"]),
    )
    assert runtime.proposed_class in {StructuralClass.ACTIVE_RUNTIME, StructuralClass.SHADOW_CANDIDATE}
    assert runtime.proposed_class != StructuralClass.UNKNOWN
