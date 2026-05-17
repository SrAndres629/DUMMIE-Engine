"""Tests for Whole-Body Scanner, Wiring Matrix, and Shadow Detector."""

import json
from pathlib import Path
from whole_body_scanner import WholeBodyScanner


def test_whole_body_scanner_execution(tmp_path):
    # Setup simulated workspace structure
    root = tmp_path
    doc_specs = root / "doc" / "specs"
    doc_specs.mkdir(parents=True, exist_ok=True)
    schemas = root / ".aiwg" / "schemas"
    schemas.mkdir(parents=True, exist_ok=True)
    reports = root / ".aiwg" / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    # Create dummy source files
    module_a = root / "layers" / "l2_brain" / "module_a.py"
    module_a.parent.mkdir(parents=True, exist_ok=True)
    module_a.write_text("import module_b\n", encoding="utf-8")

    module_b = root / "layers" / "l2_brain" / "module_b.py"
    module_b.write_text("print('hello')\n", encoding="utf-8")

    # Mapped test file
    test_a = root / "layers" / "l2_brain" / "tests" / "test_module_a.py"
    test_a.parent.mkdir(parents=True, exist_ok=True)
    test_a.write_text("def test_a(): pass\n", encoding="utf-8")

    # Spec file referencing module_a
    spec_a = doc_specs / "101_spec_a.md"
    spec_a.write_text("---\nspec_id: \"101\"\ntitle: \"Spec A\"\nstatus: \"ACTIVE\"\nlayer: \"L2\"\nlast_verified_on: \"2026-05-16\"\n---\n## Purpose\nSpec mapping\n## Physical Evidence\n`layers/l2_brain/module_a.py`\n", encoding="utf-8")

    # Schema
    schema_a = schemas / "module_a.schema.json"
    schema_a.write_text("{}", encoding="utf-8")

    # Scanner run
    scanner = WholeBodyScanner(root=root)
    res = scanner.run_scan()

    # Assert metrics
    metrics = res["metrics"]
    assert metrics["total_python_files"] == 3  # module_a, module_b, test_module_a
    assert metrics["total_spec_files"] == 1
    assert metrics["total_schema_files"] == 1

    # Assert matrix linkages
    matrix = res["matrix"]
    # module_a assertions
    rel_a = "layers/l2_brain/module_a.py"
    assert rel_a in matrix
    stats_a = matrix[rel_a]
    assert stats_a["coherence_score"] > 0
    assert "doc/specs/101_spec_a.md" in stats_a["mapped_specs"]
    assert "layers/l2_brain/tests/test_module_a.py" in stats_a["mapped_tests"]
    assert "layers/l2_brain/module_b.py" in stats_a["imports_from"]

    # module_b assertions
    rel_b = "layers/l2_brain/module_b.py"
    assert rel_b in matrix
    stats_b = matrix[rel_b]
    assert "layers/l2_brain/module_a.py" in stats_b["imported_by"]
    # module_b is imported by module_a, so it's not a shadow module
    assert stats_b["status"] != "orphaned"

    # Assert report generated
    assert (reports / "whole_body_scan_latest.json").exists()
    assert (reports / "whole_body_scan_latest.md").exists()
