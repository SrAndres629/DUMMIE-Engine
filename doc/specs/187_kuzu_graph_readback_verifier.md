---
spec_id: "187_kuzu_graph_readback_verifier"
title: "Kuzu Graph Readback Verifier"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-21"
---

## Purpose
Audit and verify the physical readback capability of the Kùzu Graph database to ensure that data written to `.aiwg/memory/kuzu_4d` is authentic, retrievable, and idempotent.

## Current State
Active. Canonical Kùzu path is `.aiwg/memory/kuzu_4d` and verification must be non-destructive against sovereign memory.

## Physical Evidence
- Core module: `layers/l2_brain/memory/kuzu_graph_readback_verifier.py`
- Compatibility module: `layers/l2_brain/memory/kuzu_graph_readback_verifier.py`
- Repository: `layers/l2_brain/infrastructure/kuzu.py`
- Test suite: `layers/l2_brain/tests/test_kuzu_graph_readback_verifier.py`
- Path hardening tests: `layers/l2_brain/tests/infrastructure/test_kuzu_path_hardening.py`
- JSON Schema: `.aiwg/schemas/kuzu_graph_readback_verification.schema.json`
- Output reports: `.aiwg/reports/kuzu_graph_readback_verification_latest.json` and `.aiwg/reports/kuzu_graph_readback_verification_latest.md`

## Contract Invariants
- **Sandbox-Isolation for Writes**: Write tests must only target a temporary, sandboxed database file, never the active `.aiwg/memory/kuzu_4d`.
- **Read-Only Sovereign Access**: Interacting with `.aiwg/memory/kuzu_4d` must strictly use read-only operations unless the caller explicitly performs a persistence flow.
- **No Lock Deletion**: Repository initialization must not delete DB files or Kùzu lock files. Lock contention is a concurrency boundary and must fail explicitly.
- **Idempotency Gate**: Re-verifying readback must yield consistent results without duplicate node or edge creations.

## Verification
Run tests via pytest:
```bash
PYTHONDONTWRITEBYTECODE=1 uv run pytest layers/l2_brain/tests/test_kuzu_graph_readback_verifier.py layers/l2_brain/tests/infrastructure/test_kuzu_path_hardening.py -q
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2.3)
- Contract Schema: `kuzu_graph_readback_verification.schema.json`
