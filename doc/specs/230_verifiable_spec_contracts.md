---
status: Draft
claims: []
implementations:
  - file: layers/l1_nervous/tools.py
    function: verify_spec / verify_all
    type: primary
---

# Verifiable Spec Contracts

**Spec ID:** 230
**Status:** Draft
**Date:** 2026-05-26
**Layer:** Documentation infrastructure

## 1. Problem

DUMMIE Engine has 47+ spec documents. LLM agents consuming them face:

1. **No trust** — A spec says "X is immutable." Is it enforced in code? Are tests passing?
2. **No discoverability** — Finding all specs about memory requires grep across 5 directories.
3. **No coherence** — Spec A says X, Spec B says not-X. No machine can detect contradictions.

## 2. Solution

Every spec gains **YAML frontmatter** with **verifiable claims**. Each claim has a shell command that proves/disproves it. A `verify_spec` action in `dummie_admin` runs claims and reports PASS/FAIL.

## 3. Format

```yaml
---
id: "02"
title: "Memory Engine 4D-TES"
status: implemented       # vision | draft | implemented | deprecated
layer: L2
depends_on: ["12"]
implements: ["models.py", "memory_ipc.py"]

claims:
  - id: "immutability"
    description: "MemoryNode4D.causal_hash is computed once and never modified"
    verify_cmd: "uv run pytest tests/test_memory_ipc_typed.py::test_immutable_node -q"
    
integrity:
  last_verified: null
  claims_passing: 0
  claims_total: 1
---
```

### 3.1 status lifecycle
- `vision`: Idea only, no formal spec, no claims.
- `draft`: Spec written, no implementation. Claims may exist without verify_cmd.
- `implemented`: Code exists + tests pass. All claims have verify_cmd.
- `deprecated`: No longer relevant. Move to `doc/.deprecated/`.

## 4. Verification Tool

Implemented in `dummie_admin`: `verify_spec(spec_id)` and `verify_all()`.

Reads spec frontmatter, extracts claims, runs `verify_cmd` via subprocess, reports PASS/FAIL.
