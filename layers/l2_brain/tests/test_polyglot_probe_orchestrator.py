"""Behavioral tests for the Polyglot Probe Orchestrator."""

import pytest
from layers.l2_brain.polyglot_probe_orchestrator import run_polyglot_probe
from layers.l2_brain.tests.test_cognitive_circulation_kernel import tmp_aiwg_root

def test_polyglot_probe_orchestrator_behavior(tmp_aiwg_root):
    """Verify run_polyglot_probe scans workspace safely."""
    # Create polyglot files
    (tmp_aiwg_root / "main.py").write_text("import sys", encoding="utf-8")
    (tmp_aiwg_root / "main.go").write_text("package main", encoding="utf-8")
    (tmp_aiwg_root / "main.rs").write_text("fn main() {}", encoding="utf-8")
    
    res = run_polyglot_probe(aiwg_root=tmp_aiwg_root)
    assert res["decision"] in ("PASS", "PASS_WITH_WARNINGS")
    assert "languages" in res
    assert "python" in res["languages"]
    assert "go" in res["languages"]
    assert "rust" in res["languages"]
    assert "first_party_files" in res
    assert len(res["first_party_files"]) >= 3
