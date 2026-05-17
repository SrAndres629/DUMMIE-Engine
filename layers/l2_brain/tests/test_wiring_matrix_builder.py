"""Tests for Wiring Matrix Builder."""

import json
from pathlib import Path
from wiring_matrix_builder import run_wiring_matrix_builder


def test_wiring_matrix_builder_execution(tmp_path):
    reports = tmp_path / ".aiwg" / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    # Create mock scan output
    scan_data = {
        "matrix": {
            "layers/l2_brain/module_x.py": {
                "imports_from": ["layers/l2_brain/module_y.py"],
                "imported_by": [],
                "mapped_specs": ["doc/specs/spec_x.md"],
                "mapped_tests": ["layers/l2_brain/tests/test_module_x.py"],
                "coherence_score": 100.0,
                "status": "active"
            },
            "layers/l2_brain/module_y.py": {
                "imports_from": [],
                "imported_by": ["layers/l2_brain/module_x.py"],
                "mapped_specs": [],
                "mapped_tests": [],
                "coherence_score": 50.0,
                "status": "active"
            }
        }
    }
    (reports / "whole_body_scan_latest.json").write_text(json.dumps(scan_data), encoding="utf-8")

    # Run builder
    res = run_wiring_matrix_builder(aiwg_root=tmp_path)

    assert res["decision"] == "PASS"
    assert len(res["nodes"]) == 2
    assert len(res["edges"]) == 3

    # Verify edge info
    edge = res["edges"][0]
    assert edge["from"] == "layers/l2_brain/module_x.py"
    assert edge["to"] == "layers/l2_brain/module_y.py"

    # Verify anomalies
    anomalies = res["anomaly_summary"]
    assert "layers/l2_brain/module_y.py" in anomalies["source_without_tests"]

    # Assert reports created
    assert (reports / "wiring_matrix_latest.json").exists()
    assert (reports / "wiring_matrix_latest.md").exists()
