---
spec_id: "187_kuzu_graph_readback_verifier"
title: "Kuzu Graph Readback Verifier"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
---

## Purpose
Audit and verify the physical readback capability of the Kùzu Graph database to ensure that data written to `.aiwg/memory/loci.db` is authentic, retrievable, and idempotent.

## Current State
Under implementation.

## Physical Evidence
- Core module: `layers/l2_brain/flat_brain/kuzu_graph_readback_verifier.py`
- Test suite: `layers/l2_brain/tests/test_kuzu_graph_readback_verifier.py`
- JSON Schema: `.aiwg/schemas/kuzu_graph_readback_verification.schema.json`
- Output reports: `.aiwg/reports/kuzu_graph_readback_verification_latest.json` and `.aiwg/reports/kuzu_graph_readback_verification_latest.md`

## Contract Invariants
- **Sandbox-Isolation for Writes**: Write tests must only target a temporary, sandboxed database directory, never the active loci.db.
- **Read-Only Loci Access**: Interacting with loci.db must strictly use read-only operations to prevent data corruption or locking exceptions.
- **Idempotency Gate**: Re-verifying readback must yield consistent results without duplicate node or edge creations.

## Verification
Run tests via pytest:
```bash
layers/l2_brain/.venv/bin/python -m pytest layers/l2_brain/tests/test_kuzu_graph_readback_verifier.py
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2.3)
- Contract Schema: `kuzu_graph_readback_verification.schema.json`
