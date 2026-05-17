---
spec_id: "166_heartbeat_decision_policy"
title: "166 Heartbeat Decision Policy"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "heartbeat_0_lifecycle"
last_verified_on: "2026-05-16"
---

# Spec 166: Heartbeat Decision Policy

## Purpose
Selects next safe actions from the self-improvement queue and classifies dispatch targets.

## Scope
- Enforces blockers (e.g. autonomous_scaling) and overrides actions based on evidence/degradations.

## Current State
- Active. Created by Heartbeat-0.

## Physical Evidence
- `layers/l2_brain/heartbeat_decision_policy.py`
- `.aiwg/reports/heartbeat_decision_policy_latest.json`

## Contract Invariants
- blocked actions are never selected
- critical actions (repair_kuzu) beat high/medium actions
- forces local advisory mode or human review dispatch if Kuzu is DEGRADED

## Verification
```bash
pytest layers/l2_brain/tests/test_heartbeat_decision_policy.py
```

## Traceability
- HEARTBEAT-0 Module 3
