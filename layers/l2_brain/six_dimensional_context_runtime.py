# Spec: 172_six_dimensional_context_runtime
# Spec: DE-V2-L2-172
"""Six-Dimensional Context Runtime Module for compiling workspace metadata into surgical context packets."""

import json
import time
import uuid
import datetime
from pathlib import Path

class SixDContextAxis:
    TEMPORAL = "temporal"
    SEMANTIC = "semantic"
    ONTOLOGICAL = "ontological"
    CAUSAL = "causal"
    AUTHORITY_SAFETY = "authority_safety"
    RESOURCE = "resource"

def build_6d_context_packet(intent: str, aiwg_root: Path = None) -> dict:
    if aiwg_root is None:
        aiwg_root = Path(__file__).resolve().parents[2]
    
    reports_dir = aiwg_root / ".aiwg" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    evidence_refs = []
    warnings = []
    decision = "PASS"
    stale_found = False

    # Check existence and read core reports
    scanner_path = reports_dir / "whole_body_scan_latest.json"
    wiring_path = reports_dir / "wiring_matrix_latest.json"
    shadow_path = reports_dir / "shadow_runtime_classification_latest.json"
    readiness_path = reports_dir / "readiness_score_calibration_latest.json"
    token_path = reports_dir / "token_economy_benchmark_latest.json"

    scan_data = {}
    if scanner_path.exists():
        evidence_refs.append(".aiwg/reports/whole_body_scan_latest.json")
        try:
            scan_data = json.loads(scanner_path.read_text(encoding="utf-8"))
            # Check age of scanner output
            mtime = scanner_path.stat().st_mtime
            age_hours = (time.time() - mtime) / 3600.0
            if age_hours > 24.0:
                stale_found = True
                warnings.append(f"whole_body_scan_latest.json is stale (age: {age_hours:.1f}h)")
        except Exception as e:
            warnings.append(f"Failed to load scan data: {e}")

    wiring_data = {}
    if wiring_path.exists():
        evidence_refs.append(".aiwg/reports/wiring_matrix_latest.json")
        try:
            wiring_data = json.loads(wiring_path.read_text(encoding="utf-8"))
        except Exception as e:
            warnings.append(f"Failed to load wiring matrix: {e}")

    shadow_data = {}
    if shadow_path.exists():
        evidence_refs.append(".aiwg/reports/shadow_runtime_classification_latest.json")
        try:
            shadow_data = json.loads(shadow_path.read_text(encoding="utf-8"))
        except Exception as e:
            warnings.append(f"Failed to load shadow runtime data: {e}")

    readiness_data = {}
    if readiness_path.exists():
        evidence_refs.append(".aiwg/reports/readiness_score_calibration_latest.json")
        try:
            readiness_data = json.loads(readiness_path.read_text(encoding="utf-8"))
        except Exception as e:
            warnings.append(f"Failed to load readiness scores: {e}")

    token_data = {}
    if token_path.exists():
        evidence_refs.append(".aiwg/reports/token_economy_benchmark_latest.json")
        try:
            token_data = json.loads(token_path.read_text(encoding="utf-8"))
        except Exception as e:
            warnings.append(f"Failed to load token economy: {e}")

    # Build 6D Axes
    axes = {
        SixDContextAxis.TEMPORAL: {
            "freshness_status": "stale" if stale_found else "fresh",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "chronology_id": str(uuid.uuid4())[:8]
        },
        SixDContextAxis.SEMANTIC: {
            "intent_keywords": [w.lower() for w in intent.split() if len(w) > 3],
            "query_intent": intent
        },
        SixDContextAxis.ONTOLOGICAL: {
            "module_count": len(scan_data.get("matrix", {})),
            "shadow_count": len(shadow_data.get("findings", []))
        },
        SixDContextAxis.CAUSAL: {
            "edges_count": len(wiring_data.get("edges", [])),
            "anomalies_detected": len(wiring_data.get("anomaly_summary", {}).get("source_without_tests", []))
        },
        SixDContextAxis.AUTHORITY_SAFETY: {
            "daily_readiness": readiness_data.get("calibrated_scores", {}).get("daily_use_readiness", 0.0),
            "autonomy_authorized": readiness_data.get("calibrated_scores", {}).get("autonomy_readiness", 0.0) >= 8.0,
            "warnings_count": len(warnings)
        },
        SixDContextAxis.RESOURCE: {
            "total_tokens_consumed": token_data.get("benchmark_results", {}).get("total_tokens_consumed", 0),
            "max_budget_limit": 500000
        }
    }

    # Gather items based on intent keywords (surgical selection)
    items = []
    intent_words = set(axes[SixDContextAxis.SEMANTIC]["intent_keywords"])
    
    matrix = scan_data.get("matrix", {})
    for path_rel, details in matrix.items():
        # Match path name or mapped elements with intent
        path_lower = path_rel.lower()
        matched = any(w in path_lower for w in intent_words)
        
        # Also match mapped tests/specs
        if not matched:
            for spec in details.get("mapped_specs", []):
                if any(w in spec.lower() for w in intent_words):
                    matched = True
                    break
        if not matched:
            for test in details.get("mapped_tests", []):
                if any(w in test.lower() for w in intent_words):
                    matched = True
                    break

        if matched:
            items.append({
                "path": path_rel,
                "status": details.get("status", "unknown"),
                "coherence": details.get("coherence_score", 0.0),
                "mapped_specs": details.get("mapped_specs", []),
                "mapped_tests": details.get("mapped_tests", []),
                "relevance": 1.0
            })

    # Invariants gates
    if not evidence_refs:
        decision = "FAIL"
        warnings.append("No sensory evidence files are available to construct context.")
    elif stale_found or warnings:
        decision = "PASS_WITH_WARNINGS"

    # Compute estimated tokens
    raw_payload_str = json.dumps(items)
    estimated_tokens = max(1, len(raw_payload_str) // 4)
    compressed_tokens = estimated_tokens
    reduction_ratio = 1.0

    # Budget gating: compress items if estimated_tokens exceeds budget
    budget = axes[SixDContextAxis.RESOURCE]["max_budget_limit"]
    if estimated_tokens > budget:
        warnings.append(f"Estimated tokens ({estimated_tokens}) exceeds budget ({budget}). Pruning context items.")
        items = items[:int(len(items) * (budget / estimated_tokens))]
        raw_payload_str = json.dumps(items)
        compressed_tokens = max(1, len(raw_payload_str) // 4)
        reduction_ratio = float(estimated_tokens) / float(compressed_tokens)

    # Compile the final packet
    packet = {
        "packet_id": str(uuid.uuid4()),
        "intent": intent,
        "decision": decision,
        "axes": axes,
        "items": items,
        "must_preserve": [item["path"] for item in items if item.get("coherence", 0.0) > 80.0],
        "should_include": [item["path"] for item in items if item.get("coherence", 0.0) <= 80.0],
        "must_not_include": shadow_data.get("findings", []),
        "evidence_refs": evidence_refs,
        "estimated_tokens": estimated_tokens,
        "compressed_tokens": compressed_tokens,
        "reduction_ratio": reduction_ratio,
        "freshness_status": "stale" if stale_found else "fresh",
        "quality_score": 100.0 - (len(warnings) * 10.0),
        "warnings": warnings
    }

    # Save outputs
    json_path = reports_dir / "6d_context_packet_latest.json"
    json_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")

    md_lines = [
        f"# Six-Dimensional Context Packet Report",
        f"- **Packet ID**: `{packet['packet_id']}`",
        f"- **Intent**: \"{intent}\"",
        f"- **Decision**: **{decision}**",
        f"- **Estimated Tokens**: {estimated_tokens}",
        f"- **Compressed Tokens**: {compressed_tokens}",
        f"- **Reduction Ratio**: {reduction_ratio:.2f}",
        f"- **Quality Score**: {packet['quality_score']:.1f}%",
        f"",
        f"## Six Dimensions Analysis",
        f"- **Temporal**: {axes[SixDContextAxis.TEMPORAL]['freshness_status']} ({axes[SixDContextAxis.TEMPORAL]['timestamp']})",
        f"- **Semantic**: matched {len(axes[SixDContextAxis.SEMANTIC]['intent_keywords'])} keywords",
        f"- **Ontological**: {axes[SixDContextAxis.ONTOLOGICAL]['module_count']} active modules analyzed",
        f"- **Causal**: {axes[SixDContextAxis.CAUSAL]['edges_count']} wiring graph dependencies parsed",
        f"- **Authority & Safety**: daily readiness score: {axes[SixDContextAxis.AUTHORITY_SAFETY]['daily_readiness']}",
        f"- **Resource**: maximum budget: {axes[SixDContextAxis.RESOURCE]['max_budget_limit']} tokens",
        f"",
        f"## Surgical Context Items",
    ]
    for item in items:
        md_lines.append(f"- **[{item['path']}](file://{aiwg_root}/{item['path']})** (Status: `{item['status']}`, Coherence: {item['coherence']:.1f}%)")
    
    if warnings:
        md_lines.append("\n## Warnings")
        for w in warnings:
            md_lines.append(f"- [WARNING] {w}")

    md_path = reports_dir / "6d_context_packet_latest.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    return packet

def run_6d_context_demo(intent: str) -> dict:
    return build_6d_context_packet(intent=intent)

if __name__ == "__main__":
    res = run_6d_context_demo("repair Kuzu persistence")
    print(f"Decision: {res['decision']}, Items: {len(res['items'])}")
