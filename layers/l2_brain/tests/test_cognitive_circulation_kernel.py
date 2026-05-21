"""Unit/Integration tests for the Cognitive Circulation Kernel (HEARTBEAT-2)

Covers:
1. 6D Context Packet compilation
2. Context Packet optimization strategies
3. Local Hashing Memory Router index seeding
4. Non-destructive 4D-TES Preflight checks
5. Safe Human-Gated Daemon Gateway Bridge envelope creation
6. Multi-language Polyglot Probe
7. Complete circulation pipeline orchestration
"""

import json
from pathlib import Path
import pytest
from layers.l2_brain.context.six_dimensional_context_runtime import build_6d_context_packet
from layers.l2_brain.context.context_packet_optimizer import optimize_context_packet
from layers.l2_brain.embedding_mesh.embedding_memory_router import run_embedding_memory_router_demo, seed_embedding_router_indices
from layers.l2_brain.memory.four_dtes_persistence_preflight import run_4dtes_preflight
from layers.l2_brain.daemon.daemon_gateway_heartbeat_bridge import run_daemon_gateway_bridge_demo, compile_daemon_gateway_envelope
from layers.l2_brain.cognition.polyglot_probe_orchestrator import run_polyglot_probe
from layers.l2_brain.context_circulation_runtime import run_cognitive_circulation


@pytest.fixture
def tmp_aiwg_root(tmp_path):
    """Fixture to create a temporary .aiwg structure with required mock scans."""
    reports = tmp_path / ".aiwg" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    
    # Write mock python file so polyglot probe PASSes
    (tmp_path / "mock_app.py").write_text("print('hello')", encoding="utf-8")
    
    # Write mock whole_body_scan_latest.json
    scan = {
        "overall_coherence_score": 55.0,
        "systemic_coherence": 55.0,
        "scan_metrics": {
            "total_files": 100,
            "shadow_modules": 0,
            "orphaned_tests": 0,
            "stale_reports": 0,
            "unvalidated_specs": 0
        }
    }
    (reports / "whole_body_scan_latest.json").write_text(json.dumps(scan), encoding="utf-8")
    
    # Write mock whole_body_scan_calibration_latest.json
    cal = {
        "decision": "PASS",
        "calibration_score": 100
    }
    (reports / "whole_body_scan_calibration_latest.json").write_text(json.dumps(cal), encoding="utf-8")
    
    # Write mock wiring_matrix_latest.json
    wir = {
        "decision": "PASS",
        "nodes": [],
        "edges": []
    }
    (reports / "wiring_matrix_latest.json").write_text(json.dumps(wir), encoding="utf-8")
    
    # Write mock shadow_runtime_classification_latest.json
    sha = {
        "decision": "PASS",
        "findings": []
    }
    (reports / "shadow_runtime_classification_latest.json").write_text(json.dumps(sha), encoding="utf-8")
    
    return tmp_path


def test_six_dimensional_context_runtime(tmp_aiwg_root):
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


def test_context_packet_optimizer(tmp_aiwg_root):
    """Verify that context_packet_optimizer optimizes a packet with ratio > 1.0."""
    packet = build_6d_context_packet(intent="refactor system", aiwg_root=tmp_aiwg_root)
    optimized = optimize_context_packet(packet=packet, aiwg_root=tmp_aiwg_root)
    assert optimized["decision"] in ("PASS", "PASS_WITH_WARNINGS")
    assert optimized["reduction_ratio"] >= 1.0
    assert "selected_strategy" in optimized
    assert "optimized_tokens" in optimized


def test_embedding_memory_router(tmp_aiwg_root):
    """Verify that seed_embedding_router_indices seeds hashes correctly."""
    # Seed files in reports to generate items in context packet
    reports = tmp_aiwg_root / ".aiwg" / "reports"
    packet = build_6d_context_packet(intent="optimize db query", aiwg_root=tmp_aiwg_root)
    (reports / "6d_context_packet_latest.json").write_text(json.dumps(packet), encoding="utf-8")

    indices = seed_embedding_router_indices(tmp_aiwg_root)
    assert "vectors" in indices
    assert "fallback_mode" in indices
    assert indices["fallback_mode"] == "DETERMINISTIC_FALLBACK"
    
    demo = run_embedding_memory_router_demo(intent="optimize db query", aiwg_root=tmp_aiwg_root)
    assert demo["decision"] in ("PASS", "PASS_WITH_WARNINGS")
    assert "results" in demo


def test_four_dtes_persistence_preflight(tmp_aiwg_root):
    """Verify that run_4dtes_preflight runs logical simulation checks without mutations."""
    res = run_4dtes_preflight(aiwg_root=tmp_aiwg_root)
    assert "decision" in res
    assert "spine_status" in res or "memory_spine_status" in res
    assert "write_mode" in res or "graph_write_mode" in res
    assert "blocked_actions" in res
    assert "repair_plan" in res


def test_daemon_gateway_heartbeat_bridge(tmp_aiwg_root):
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


def test_polyglot_probe_orchestrator(tmp_aiwg_root):
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


def test_context_circulation_runtime(tmp_aiwg_root):
    """Verify the context_circulation orchestrator runs the entire loop correctly."""
    # Create polyglot files for loop
    (tmp_aiwg_root / "main.py").write_text("import sys", encoding="utf-8")
    (tmp_aiwg_root / "main.go").write_text("package main", encoding="utf-8")
    (tmp_aiwg_root / "main.rs").write_text("fn main() {}", encoding="utf-8")
    
    res = run_cognitive_circulation(intent="full validation", aiwg_root=tmp_aiwg_root)
    assert "six_d_context" in res
    assert "context_optimization" in res
    assert "embedding_memory" in res
    assert "four_dtes_preflight" in res
    assert "daemon_gateway_bridge" in res
    assert "polyglot_probe" in res
    
    assert res["six_d_context"]["decision"] in ("PASS", "PASS_WITH_WARNINGS")
    assert res["context_optimization"]["decision"] in ("PASS", "PASS_WITH_WARNINGS")
    assert res["embedding_memory"]["decision"] in ("PASS", "PASS_WITH_WARNINGS")
    assert res["four_dtes_preflight"]["decision"] in ("PASS", "PASS_WITH_WARNINGS")
    assert res["daemon_gateway_bridge"]["decision"] in ("PASS", "PASS_WITH_WARNINGS")
    assert res["polyglot_probe"]["decision"] in ("PASS", "PASS_WITH_WARNINGS")
