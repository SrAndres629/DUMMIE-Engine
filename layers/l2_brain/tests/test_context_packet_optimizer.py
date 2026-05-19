import json
import pytest
from layers.l2_brain.context_packet_optimizer import optimize_context_packet
from layers.l2_brain.six_dimensional_context_runtime import build_6d_context_packet
from layers.l2_brain.tests.test_cognitive_circulation_kernel import tmp_aiwg_root

def test_context_packet_optimizer_direct(tmp_aiwg_root):
    """Verify that context_packet_optimizer optimizes a packet with reduction assertions."""
    packet = build_6d_context_packet(intent="refactor system", aiwg_root=tmp_aiwg_root)
    optimized = optimize_context_packet(packet=packet, aiwg_root=tmp_aiwg_root)
    assert optimized["decision"] in ("PASS", "PASS_WITH_WARNINGS")
    assert optimized["reduction_ratio"] >= 1.0
    assert "selected_strategy" in optimized
    assert "optimized_tokens" in optimized
    assert isinstance(optimized["optimized_tokens"], int)
