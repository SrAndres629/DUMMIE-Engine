from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_specs_docs.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_specs_docs", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_extract_direct_spec_refs_parses_spec_reference_line() -> None:
    validator = _load_validator()

    refs = validator.extract_direct_spec_refs(
        "# Spec Reference: 192_embedding_mesh_foundation, DE-V2-L2-201\n"
        "print('hello')\n"
    )

    assert refs == ["192_embedding_mesh_foundation", "DE-V2-L2-201"]


def test_source_has_direct_spec_link_accepts_spec_id_or_file_stem(
    tmp_path: Path,
) -> None:
    validator = _load_validator()
    source = tmp_path / "module.py"
    source.write_text(
        "# Spec Reference: 201_canonical_spec_binding_registry\n", encoding="utf-8"
    )

    assert validator.source_has_direct_spec_link(
        source,
        {"DE-V2-L2-201", "201_canonical_spec_binding_registry"},
    )


def test_build_direct_linkage_report_counts_bound_runtime_files() -> None:
    validator = _load_validator()

    report = validator.build_direct_linkage_report(ROOT)

    assert report["bound_active_runtime_count"] > 0
    assert (
        0 <= report["direct_spec_linked_count"] <= report["bound_active_runtime_count"]
    )
    assert 0.0 <= report["direct_spec_hit_rate"] <= 1.0
    assert "unlinked_bound_runtime" in report


def test_cli_report_direct_linkage_outputs_metric() -> None:
    res = subprocess.run(
        [sys.executable, "scripts/validate_specs_docs.py", "--report-direct-linkage"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert res.returncode in (0, 1)
    assert "direct_spec_hit_rate=" in res.stdout


def test_cli_strict_direct_linkage_only_passes_when_bound_runtime_is_linked() -> None:
    res = subprocess.run(
        [
            sys.executable,
            "scripts/validate_specs_docs.py",
            "--direct-linkage-only",
            "--strict-direct-linkage",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert res.returncode == 0
    assert "direct_spec_hit_rate=1.0" in res.stdout
