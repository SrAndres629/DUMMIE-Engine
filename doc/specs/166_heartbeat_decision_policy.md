---
spec_id: 166_heartbeat_decision_policy
title: 166 Heartbeat Decision Policy
status: ACTIVE
canonicality: canonical
artifact_type: spec
plan: DUMMIE PLAN V1
layer: l2_brain
created_by: heartbeat_0_lifecycle
last_verified_on: '2026-05-16'
claims:
- id: 166_heartbeat_decision_policy-file-valid
  description: Spec file '166_heartbeat_decision_policy.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/166_heartbeat_decision_policy.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
# Spec 166: Heartbeat Decision Policy

## Purpose
Selects next safe actions from the self-improvement queue and classifies dispatch targets.

## Scope
- Enforces blockers (e.g. autonomous_scaling) and overrides actions based on evidence/degradations.

## Current State
- Active. Created by Heartbeat-0.

## Physical Evidence
- `layers/l2_brain/heartbeat/heartbeat_decision_policy.py`
- `.aiwg/reports/heartbeat_decision_policy_latest.json`

## Contract Invariants
- blocked actions are never selected
- critical actions (repair_kuzu) beat high/medium actions
- may dispatch autonomously. If Kuzu is DEGRADED, repair is prioritized.

## Verification
```bash
pytest layers/l2_brain/tests/test_heartbeat_decision_policy.py
```

## Traceability
- HEARTBEAT-0 Module 3
