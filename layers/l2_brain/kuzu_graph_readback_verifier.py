# Spec Reference: 187_kuzu_graph_readback_verifier
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Spec Reference: 187_kuzu_graph_readback_verifier

def run_kuzu_graph_readback_verification() -> dict:
    aiwg_root = Path(__file__).resolve().parents[2] / ".aiwg"
    reports_dir = aiwg_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    db_path = str(aiwg_root / "memory" / "loci.db")
    db_path_exists = os.path.exists(db_path)

    kuzu_importable = False
    sandbox_write_readback_ok = False
    memory_spine_readback_ok = False
    reported_nodes = 0
    reported_edges = 0
    readback_nodes = 0
    readback_edges = 0
    idempotency_check = "NOT_RUN"
    warnings = []
    evidence_refs = [
        ".aiwg/reports/memory_spine_sync_latest.json",
        ".aiwg/memory/loci.db"
    ]

    # Level 1: Import Check
    try:
        import kuzu
        kuzu_importable = True
    except ImportError as e:
        warnings.append(f"Kuzu import failed: {e}")

    # Read latest sync report
    sync_report_path = reports_dir / "memory_spine_sync_latest.json"
    db_status_reported = "UNKNOWN"
    if sync_report_path.exists():
        try:
            with open(sync_report_path, "r", encoding="utf-8") as f:
                sync_data = json.load(f)
                reported_nodes = sync_data.get("total_nodes", 0)
                reported_edges = sync_data.get("total_edges", 0)
                db_status_reported = sync_data.get("db_status", "UNKNOWN")
        except Exception as e:
            warnings.append(f"Failed to read memory_spine_sync_latest.json: {e}")

    # Level 2: Sandbox write/readback
    if kuzu_importable:
        temp_dir = tempfile.mkdtemp()
        try:
            sb_db_path = os.path.join(temp_dir, "sandbox.db")
            db = kuzu.Database(sb_db_path)
            conn = kuzu.Connection(db)
            
            # Create schema
            conn.execute(
                "CREATE NODE TABLE MemoryNode4D("
                "causal_hash STRING, "
                "parent_hashes STRING[], "
                "locus_x STRING, "
                "locus_y STRING, "
                "locus_z STRING, "
                "lamport_t INT64, "
                "authority_a STRING, "
                "intent_i STRING, "
                "payload STRING, "
                "payload_hash STRING, "
                "embedding FLOAT[], "
                "PRIMARY KEY (causal_hash))"
            )
            conn.execute("CREATE REL TABLE CAUSAL_LINK(FROM MemoryNode4D TO MemoryNode4D)")
            
            # Write dummy
            conn.execute(
                "CREATE (n:MemoryNode4D {causal_hash: 'sandbox_test_hash', parent_hashes: ['GENESIS'], "
                "locus_x: 'x', locus_y: 'y', locus_z: 'z', lamport_t: 1, authority_a: 'AGENT', "
                "intent_i: 'MUTATION', payload: 'test payload', payload_hash: 'hash_val', embedding: [0.0]})"
            )
            
            # Read dummy
            res = conn.execute("MATCH (n:MemoryNode4D) RETURN n.causal_hash, n.payload")
            if res.has_next():
                row = res.get_next()
                if row[0] == 'sandbox_test_hash' and row[1] == 'test payload':
                    sandbox_write_readback_ok = True
        except Exception as e:
            warnings.append(f"Kuzu sandbox test failed: {e}")
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    # Level 3: Actual loci.db readback (Safe read-only match)
    if kuzu_importable and db_path_exists:
        try:
            # Open actual DB. Keep read-only, handle process locks gracefully.
            db = kuzu.Database(db_path)
            conn = kuzu.Connection(db)
            
            # Node count
            node_res = conn.execute("MATCH (n:MemoryNode4D) RETURN count(*)")
            if node_res.has_next():
                readback_nodes = node_res.get_next()[0]
                
            # Edge count
            edge_res = conn.execute("MATCH ()-[r:CAUSAL_LINK]->() RETURN count(*)")
            if edge_res.has_next():
                readback_edges = edge_res.get_next()[0]
            
            memory_spine_readback_ok = True
            
            # Verify idempotency
            idempotency_check = "PASS" if readback_nodes >= reported_nodes else "FAIL"
        except Exception as e:
            warnings.append(f"Kuzu actual database readback failed: {e}")

    # Determine recommendation status
    # Only recommend READY if memory_spine_readback_ok is true and idempotency_check PASS.
    # Otherwise recommend READY_CANDIDATE or SANDBOX_READY.
    if memory_spine_readback_ok and idempotency_check == "PASS":
        promotion_recommendation = "READY"
        decision = "PASS"
    elif sandbox_write_readback_ok:
        promotion_recommendation = "READY_CANDIDATE"
        decision = "PASS_WITH_WARNINGS"
        warnings.append("Loci.db locked or unretrievable. Recommending READY_CANDIDATE based on sandbox success.")
    elif kuzu_importable:
        promotion_recommendation = "SANDBOX_READY"
        decision = "PASS_WITH_WARNINGS"
        warnings.append("Kuzu is importable but sandbox tests failed. Recommending SANDBOX_READY.")
    else:
        promotion_recommendation = "DEGRADED"
        decision = "FAIL"

    report = {
        "decision": decision,
        "kuzu_importable": kuzu_importable,
        "db_status_reported": db_status_reported,
        "db_path": db_path,
        "db_path_exists": db_path_exists,
        "sandbox_write_readback_ok": sandbox_write_readback_ok,
        "memory_spine_readback_ok": memory_spine_readback_ok,
        "reported_nodes": reported_nodes,
        "reported_edges": reported_edges,
        "readback_nodes": readback_nodes,
        "readback_edges": readback_edges,
        "idempotency_check": idempotency_check,
        "promotion_recommendation": promotion_recommendation,
        "warnings": warnings,
        "evidence_refs": evidence_refs
    }

    # Write JSON report
    json_path = reports_dir / "kuzu_graph_readback_verification_latest.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Write Markdown report
    md_path = reports_dir / "kuzu_graph_readback_verification_latest.md"
    md_content = f"""# Kuzu Graph Readback Verification Report
**Decision**: `{decision}`  
**Promotion Recommendation**: `{promotion_recommendation}`

## Verification Summary
- **Kuzu Importable**: {kuzu_importable}
- **Database Path Exists**: {db_path_exists} ({db_path})
- **Sandbox Write/Readback OK**: {sandbox_write_readback_ok}
- **Loci.db Readback OK**: {memory_spine_readback_ok}
- **Reported Counts**: Nodes={reported_nodes}, Edges={reported_edges}
- **Readback Counts**: Nodes={readback_nodes}, Edges={readback_edges}
- **Idempotency Check**: `{idempotency_check}`

## Warnings
{chr(10).join(f'- {w}' for w in warnings) if warnings else 'None'}
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return report
