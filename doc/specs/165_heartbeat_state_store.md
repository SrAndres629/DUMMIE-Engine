---
spec_id: "165_heartbeat_state_store"
title: "165 Heartbeat State Store"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "heartbeat_0_lifecycle"
last_verified_on: "2026-05-16"
---

# Spec 165: Heartbeat State Store

## Purpose
Manages append-only JSONL ledger for heartbeat history.

## Scope
- Maintains latest, seed and index files for heartbeat history idempotently without private CoT.

## Current State
- Active. Created by Heartbeat-0.

## Physical Evidence
- `layers/l2_brain/heartbeat/heartbeat_state_store.py`
- `.aiwg/heartbeat/heartbeat_ledger.jsonl`

## Contract Invariants
- append is idempotent by heartbeat_id
- updates latest and next_heartbeat_seed atomically
- contains no private reasoning keys or secrets

## Verification
```bash
pytest layers/l2_brain/tests/test_heartbeat_state_store.py
```

## Traceability
- HEARTBEAT-0 Module 2
