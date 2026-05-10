import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT.parents[0] / "l2_brain"
for path in (ROOT, L2):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from tools_impl.sdd import SDDToolService


def test_sdd_admission_blocks_missing_parent_spec():
    service = SDDToolService()

    result = service.evaluate_change_admission(
        files=["layers/l2_brain/models.py"],
        intent="edit model",
        parent_spec_ids=[],
        specs=[],
        evidence=[],
        risk="medium",
    )

    assert result["status"] == "BLOCK"


def test_sdd_golden_path_requires_approved_spec():
    service = SDDToolService()

    result = service.generate_golden_path(
        spec_id="sdd",
        approved=False,
        target_module="layers/l2_brain/sdd_governance.py",
    )

    assert result["allowed"] is False


def test_sdd_runtime_guard_blocks_unready_provider():
    service = SDDToolService()

    result = service.evaluate_runtime_guard(
        provider_ready=False,
        memory_locked=False,
        parent_spec_approved=True,
        l3_policy="ALLOWED",
    )

    assert result["status"] == "BLOCK"
    assert "provider_not_ready" in result["reasons"]
