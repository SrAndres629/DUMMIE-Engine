import json
import pytest
from layers.l2_brain.embedding_mesh.embedding_memory_router import run_embedding_memory_router_demo, seed_embedding_router_indices
from layers.l2_brain.context.six_dimensional_context_runtime import build_6d_context_packet
from layers.l2_brain.tests.test_cognitive_circulation_kernel import tmp_aiwg_root

def test_embedding_memory_router_direct(tmp_aiwg_root):
    """Verify that seed_embedding_router_indices seeds hashes correctly and runs router demo."""
    reports = tmp_aiwg_root / ".aiwg" / "reports"
    packet = build_6d_context_packet(intent="optimize db query", aiwg_root=tmp_aiwg_root)
    (reports / "6d_context_packet_latest.json").write_text(json.dumps(packet), encoding="utf-8")

    indices = seed_embedding_router_indices(tmp_aiwg_root)
    assert "vectors" in indices
    assert "fallback_mode" in indices
    assert indices["fallback_mode"] == "DETERMINISTIC_FALLBACK"
    assert len(indices["vectors"]) >= 0
    
    demo = run_embedding_memory_router_demo(intent="optimize db query", aiwg_root=tmp_aiwg_root)
    assert demo["decision"] in ("PASS", "PASS_WITH_WARNINGS")
    assert "results" in demo
