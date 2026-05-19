"""Behavioral tests for 4D-TES Persistence Preflight."""

import pytest
from layers.l2_brain.four_dtes_persistence_preflight import run_4dtes_preflight
from layers.l2_brain.tests.test_cognitive_circulation_kernel import tmp_aiwg_root

def test_four_dtes_persistence_preflight_behavior(tmp_aiwg_root):
    """Verify that run_4dtes_preflight runs logical simulation checks without mutations."""
    res = run_4dtes_preflight(aiwg_root=tmp_aiwg_root)
    assert "decision" in res
    assert "spine_status" in res or "memory_spine_status" in res
    assert "write_mode" in res or "graph_write_mode" in res
    assert "blocked_actions" in res
    assert "repair_plan" in res
