"""Behavioral tests for the Daemon Gateway Heartbeat Bridge."""

import pytest
from layers.l2_brain.daemon_gateway_heartbeat_bridge import compile_daemon_gateway_envelope, run_daemon_gateway_bridge_demo
from layers.l2_brain.tests.test_cognitive_circulation_kernel import tmp_aiwg_root

def test_daemon_gateway_heartbeat_bridge_behavior(tmp_aiwg_root):
    """Verify compile_daemon_gateway_envelope structures a valid human-gated envelope."""
    envelope = compile_daemon_gateway_envelope(
        intent="mutate source file",
        safety_status={"overall_coherence_score": 55.0},
        aiwg_root=tmp_aiwg_root
    )
    assert envelope["decision"] in ("PASS", "PASS_WITH_WARNINGS")
    assert "bridge_envelope" in envelope
    bridge = envelope["bridge_envelope"]
    assert bridge["requires_human_approval"] is True
    assert bridge["can_execute_now"] is False
    
    # Demo query
    demo = run_daemon_gateway_bridge_demo(intent="safe read action", aiwg_root=tmp_aiwg_root)
    assert demo["decision"] in ("PASS", "PASS_WITH_WARNINGS")
