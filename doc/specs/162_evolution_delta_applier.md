---
spec_id: "162_evolution_delta_applier"
title: "162 Evolution Delta Applier"
status: "DEPRECATED"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "operationalization_pack_5_2_2"
last_verified_on: "2026-05-16"
---

# Spec 162: Evolution Delta Applier

## Purpose
Transform philosophical evolution deltas into prioritised operational actions.

## Scope
- Reads evolution deltas, bias reports and hygiene results to generate actionable improvement items.

## Current State
- Operational. Created by Pack 5.2.2.

## Physical Evidence
- `.aiwg/reports/evolution_delta_application_latest.json`

## Contract Invariants
- blocks autonomous_scaling while Kuzu DEGRADED
- generates repair_kuzu_persistence as critical action
- never mutates state directly

## Verification
```bash
pytest layers/l2_brain/tests/test_evolution_delta_applier.py
```

## Traceability
- POST_PLAN_V1_OPERATIONALIZATION_PACK_5_2_2 Module 2
