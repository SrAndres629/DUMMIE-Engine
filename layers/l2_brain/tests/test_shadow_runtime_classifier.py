"""Tests for Shadow Runtime Classifier."""

import json
from pathlib import Path
from shadow_runtime_classifier import run_shadow_runtime_classifier


def test_shadow_runtime_classifier_execution(tmp_path):
    reports = tmp_path / ".aiwg" / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    # Create mock scan output where module_z is an orphan/shadow module
    scan_data = {
        "findings": {
            "shadow_modules": ["layers/l2_brain/module_z.py"]
        },
        "matrix": {
            "layers/l2_brain/module_z.py": {
                "imports_from": [],
                "imported_by": [],
                "mapped_specs": [],
                "mapped_tests": [],
                "coherence_score": 0.0,
                "status": "orphaned"
            }
        }
    }
    (reports / "whole_body_scan_latest.json").write_text(json.dumps(scan_data), encoding="utf-8")

    # Create dummy file to simulate actual existence
    module_z = tmp_path / "layers" / "l2_brain" / "module_z.py"
    module_z.parent.mkdir(parents=True, exist_ok=True)
    module_z.write_text("class LegacyExecutor:\n    pass\n", encoding="utf-8")

    # Run classifier
    res = run_shadow_runtime_classifier(aiwg_root=tmp_path)

    assert res["decision"] == "PASS"
    assert len(res["findings"]) == 1
    finding = res["findings"][0]
    assert finding["path"] == "layers/l2_brain/module_z.py"
    assert finding["classification"] == "orphan_candidate"

    # Assert report files created
    assert (reports / "shadow_runtime_classification_latest.json").exists()
    assert (reports / "shadow_runtime_classification_latest.md").exists()
