---
spec_id: "166_l2_brain_organ_migration_contract"
title: "L2 Brain Organ Migration Contract"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "PACK_R4"
layer: "l2_brain"
created_by: "codex"
created_on: "2026-05-19"
last_verified_on: "2026-05-19"
depends_on:
  - "165_cognitive_lifecycle_contract"
---

# Spec 166: L2 Brain Organ Migration Contract

## Purpose
Define the canonical closure criteria for PACK R4 migration away from the monolithic `flat_brain/` runtime layout into explicit L2 organs.

## Current State
PACK R4 organ migration is active and physically represented in `layers/l2_brain/`.

The runtime now exposes canonical organ directories for context, memory, cognition, daemon, model mesh, governance, infrastructure, mission, metacognition, heartbeat, strategic, SDK, proto, domain, and structural hardening.

`layers/l2_brain/flat_brain/` still exists as a legacy compatibility source. It is not the canonical destination for new code and must not be used directly by canonical organs.

## Canonical Organ Policy
- New L2 code must live in a named organ directory or a root compatibility wrapper.
- Public imports such as `layers.l2_brain.model_router` must resolve outside `flat_brain/`.
- `flat_brain/` may remain as a compatibility fallback while legacy modules are migrated incrementally.
- Canonical organs must not import `layers.l2_brain.flat_brain.*` directly.
- The root package may contain compatibility logic that falls back to `flat_brain/` only for modules without a canonical organ equivalent.
- Tests must guard public module resolution and direct flat dependencies.

## Public Compatibility Modules
The following root modules are canonical public compatibility wrappers:

- `layers/l2_brain/action_graph.py`
- `layers/l2_brain/token_cost_ledger.py`
- `layers/l2_brain/neuron_ledger.py`
- `layers/l2_brain/model_router.py`
- `layers/l2_brain/model_discovery.py`
- `layers/l2_brain/model_executor.py`
- `layers/l2_brain/supervisor_protocol.py`

## Physical Evidence
- `layers/l2_brain/__init__.py`
- `layers/l2_brain/action_graph.py`
- `layers/l2_brain/token_cost_ledger.py`
- `layers/l2_brain/neuron_ledger.py`
- `layers/l2_brain/model_router.py`
- `layers/l2_brain/model_discovery.py`
- `layers/l2_brain/model_executor.py`
- `layers/l2_brain/supervisor_protocol.py`
- `layers/l2_brain/cognition/action_graph.py`
- `layers/l2_brain/model_mesh/token_cost_ledger.py`
- `layers/l2_brain/model_mesh/neuron_ledger.py`
- `layers/l2_brain/daemon/daemon.py`
- `layers/l2_brain/daemon/daemon_diagnostic.py`
- `layers/l2_brain/tests/test_pack_r4_flat_migration_contract.py`
- `.aiwg/state/pack_r4_flat_brain_moves.json`
- `.aiwg/state/pack_r4_move_log.json`

## Contract Invariants
- Public root modules listed in this spec must not resolve through `flat_brain/`.
- Canonical organs must not contain direct `layers.l2_brain.flat_brain` imports.
- `flat_brain/` compatibility must be explicit and isolated to the root package bridge or legacy tests.
- Migration closure is not permission to delete `flat_brain/` until all legacy-only modules have canonical equivalents and tests prove no fallback is used.
- PACK R4 can be considered structurally closed only when `test_pack_r4_flat_migration_contract.py` passes.

## Verification
```bash
PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -q layers/l2_brain/tests/test_pack_r4_flat_migration_contract.py
PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -q layers/l2_brain/tests/test_pack_r4_flat_migration_contract.py layers/l2_brain/tests/test_token_cost_ledger.py layers/l2_brain/tests/test_token_economy_integration.py layers/l2_brain/tests/test_runtime_repairs.py layers/l2_brain/tests/test_pack2_3_l2_bindings_smoke.py
```

## Traceability
| Relationship | Artifact | Role |
| --- | --- | --- |
| Governed by lifecycle contract | `.aiwg/specs/165_cognitive_lifecycle_contract.md` | Requires evidence before closure claims |
| Movement ledger | `.aiwg/state/pack_r4_flat_brain_moves.json` | Records flat module movement |
| Source-brain movement ledger | `.aiwg/state/pack_r4_move_log.json` | Records `src/brain` movement |
| Regression test | `layers/l2_brain/tests/test_pack_r4_flat_migration_contract.py` | Enforces public imports outside flat and no direct flat imports |
| Runtime bridge | `layers/l2_brain/__init__.py` | Preserves compatibility while preferring canonical organs |

