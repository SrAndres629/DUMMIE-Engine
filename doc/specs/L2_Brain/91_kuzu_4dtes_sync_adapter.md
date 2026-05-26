---
spec_id: DE-PHASE9-KSA-91
title: Kuzu Graph Sync Adapter
status: DRAFT
layer: L2
last_verified_on: '2025-05-15'
priority: MANDATORY
version: 1.0.0
namespace: dummie.engine.l2
claims:
- id: 91_kuzu_4dtes_sync_adapter-file-valid
  description: Spec file '91_kuzu_4dtes_sync_adapter.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/L2_Brain/91_kuzu_4dtes_sync_adapter.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# Kuzu Graph Sync Adapter

## Purpose
The final adapter for Kuzu/4D-TES synchronization. Provides validation and apply logic.

## Current State
Implemented in `layers/l2_brain/kuzu_graph_sync_adapter.py`. Safe apply logic with readback verification.

## Physical Evidence
- `layers/l2_brain/kuzu_graph_sync_adapter.py`
- `layers/l2_brain/tests/test_kuzu_graph_sync_adapter.py`

## Contract Invariants
- **Safety**: Writes are enabled by default (allow_write=True). Sovereign mandate.
- **Robustness**: Handles missing database as a degraded state.
- **Integrity**: Validates plan schema and node/edge structure.

## Traceability
- **Missions**: `demo_refactor_snowball`
- **Layers**: `L2_BRAIN`
- **Files**: `layers/l2_brain/kuzu_graph_sync_adapter.py`

## Verification
```bash
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_kuzu_graph_sync_adapter.py
```
