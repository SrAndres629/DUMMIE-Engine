"""Context Circulation Runtime Orchestrator Module connecting scanners, 6D packets, optimization, and gateway bridges."""

from pathlib import Path
from six_dimensional_context_runtime import build_6d_context_packet
from context_packet_optimizer import optimize_context_packet
from embedding_memory_router import run_embedding_memory_router_demo
from four_dtes_persistence_preflight import run_4dtes_preflight
from daemon_gateway_heartbeat_bridge import run_daemon_gateway_bridge_demo
from polyglot_probe_orchestrator import run_polyglot_probe

def run_cognitive_circulation(intent: str, aiwg_root: Path = None) -> dict:
    if aiwg_root is None:
        aiwg_root = Path(__file__).resolve().parents[2]

    # Step 1: Compile 6D Context Packet from active sensory scanner reports
    packet = build_6d_context_packet(intent=intent, aiwg_root=aiwg_root)

    # Step 2: Perform Context Token Optimization
    opt = optimize_context_packet(packet=packet, aiwg_root=aiwg_root)

    # Step 3: Seed deterministic memory index and query routing
    emb = run_embedding_memory_router_demo(intent=intent, aiwg_root=aiwg_root)

    # Step 4: Conduct non-destructive 4D-TES Persistence pre-flight check
    pre = run_4dtes_preflight(aiwg_root=aiwg_root)

    # Step 5: Draft safe human-gated Dispatch Envelope for gateway bridges
    bridge = run_daemon_gateway_bridge_demo(intent=intent, aiwg_root=aiwg_root)

    # Step 6: Scan workspace for multi-language components
    poly = run_polyglot_probe(aiwg_root=aiwg_root)

    # Compile unified circulation summary
    circulation_summary = {
        "intent": intent,
        "six_d_context": {
            "decision": packet.get("decision"),
            "items_count": len(packet.get("items", [])),
            "estimated_tokens": packet.get("estimated_tokens")
        },
        "context_optimization": {
            "decision": opt.get("decision"),
            "strategy": opt.get("selected_strategy"),
            "reduction_ratio": opt.get("reduction_ratio")
        },
        "embedding_memory": {
            "decision": emb.get("decision"),
            "mode": emb.get("embedding_mode"),
            "indexed_items": emb.get("indexed_items")
        },
        "four_dtes_preflight": {
            "decision": pre.get("decision"),
            "write_mode": pre.get("graph_write_mode"),
            "spine_status": pre.get("memory_spine_status")
        },
        "daemon_gateway_bridge": {
            "decision": bridge.get("decision"),
            "dispatch_id": bridge.get("dispatch_envelope", {}).get("dispatch_id"),
            "target": bridge.get("dispatch_envelope", {}).get("target")
        },
        "polyglot_probe": {
            "decision": poly.get("decision"),
            "languages": list(poly.get("languages", {}).keys())
        }
    }

    return circulation_summary
