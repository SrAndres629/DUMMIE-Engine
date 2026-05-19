"""Behavioral tests for the 6D Context Packet compilation."""

import pytest
from layers.l2_brain.six_dimensional_context_runtime import build_6d_context_packet
from layers.l2_brain.tests.test_cognitive_circulation_kernel import tmp_aiwg_root

def test_six_dimensional_context_runtime_behavior(tmp_aiwg_root):
    """Verify that build_6d_context_packet constructs a valid 6D context packet."""
    packet = build_6d_context_packet(intent="repair kuzuDB", aiwg_root=tmp_aiwg_root)
    assert packet["decision"] in ("PASS", "PASS_WITH_WARNINGS")
    assert "intent" in packet
    assert "axes" in packet
    assert "temporal" in packet["axes"]
    assert "semantic" in packet["axes"]
    assert "ontological" in packet["axes"]
    assert "causal" in packet["axes"]
    assert "authority_safety" in packet["axes"]
    assert "resource" in packet["axes"]
    assert "items" in packet
    assert "quality_score" in packet
