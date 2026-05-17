---
spec_id: "167_heartbeat_scheduler"
title: "167 Heartbeat Scheduler"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "heartbeat_0_lifecycle"
last_verified_on: "2026-05-16"
---

# Spec 167: Heartbeat Scheduler

## Purpose
Orchestrates manual scheduler execution without background processes or timers.

## Scope
- Provides once, dry-run, and seed commands for manual operators.

## Current State
- Active. Created by Heartbeat-0.

## Physical Evidence
- `layers/l2_brain/heartbeat_scheduler.py`
- `.aiwg/reports/heartbeat_scheduler_latest.json`

## Contract Invariants
- no background running timers or loops
- dry-run does not write to main ledger or mutate session learning episodes
- provides JSON outputs serializable for CLI use

## Verification
```bash
pytest layers/l2_brain/tests/test_heartbeat_scheduler.py
```

## Traceability
- HEARTBEAT-0 Module 4
