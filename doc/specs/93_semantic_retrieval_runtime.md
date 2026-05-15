---
spec_id: "DE-PHASE10-SRR-93"
title: "Semantic Retrieval Runtime"
status: "DRAFT"
layer: "L2"
last_verified_on: "2025-05-15"
priority: "MANDATORY"
---
# Semantic Retrieval Runtime

## Purpose
Orchestrates semantic retrieval operations for DUMMIE. Connects the Socraticode adapter with the ContextBudgetManager and MemoryGraphRuntime to produce standardized context packets for downstream reasoning.

## Current State
Implemented in `layers/l2_brain/semantic_retrieval_runtime.py`.

## Physical Evidence
- `layers/l2_brain/semantic_retrieval_runtime.py`
- `layers/l2_brain/tests/test_semantic_retrieval_runtime.py`
- `.aiwg/schemas/semantic_retrieval.schema.json`

## Contract Invariants
- **Schema Conformity**: Output always matches the `semantic_retrieval.schema.json`.
- **Budget Awareness**: Context must be truncated or prioritized if it exceeds the ContextBudgetManager limits.

## Traceability
- **Missions**: `demo_refactor_snowball`
- **Layers**: `L2_BRAIN`

## Verification
```bash
layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_semantic_retrieval_runtime.py
```
