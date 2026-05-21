import json
import pytest
from layers.l2_brain.context.six_dimensional_context_runtime import build_6d_context_packet
from layers.l2_brain.tests.test_cognitive_circulation_kernel import tmp_aiwg_root

def test_six_dimensional_context_runtime_direct(tmp_aiwg_root):
    """Verify that build_6d_context_packet constructs a valid 6D context packet with all required axes."""
    packet = build_6d_context_packet(intent="repair kuzuDB", aiwg_root=tmp_aiwg_root)
    assert packet["decision"] in ("PASS", "PASS_WITH_WARNINGS")
    assert "intent" in packet
    assert packet["intent"] == "repair kuzuDB"
    assert "axes" in packet
    
    # Assert physical contract invariance for all 6 axes
    axes = packet["axes"]
    for axis in ["temporal", "semantic", "ontological", "causal", "authority_safety", "resource"]:
        assert axis in axes
        assert isinstance(axes[axis], dict)
