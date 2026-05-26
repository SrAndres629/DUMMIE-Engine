---
spec_id: 164_heartbeat_lifecycle_runtime
title: 164 Heartbeat Lifecycle Runtime
status: ACTIVE
canonicality: canonical
artifact_type: spec
plan: DUMMIE PLAN V1
layer: l2_brain
created_by: heartbeat_0_lifecycle
last_verified_on: '2026-05-16'
claims:
- id: 164_heartbeat_lifecycle_runtime-file-valid
  description: Spec file '164_heartbeat_lifecycle_runtime.md' exists, parses valid
    YAML frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/164_heartbeat_lifecycle_runtime.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# Spec 164: Heartbeat Lifecycle Runtime

## Purpose
Orchestrates a full observe -> reason -> queue -> learn cycle.

## Scope
- Runs heartbeat in observe, advisory, repair_planning, execute, or autonomous mode. May mutate system within mission contract scope.

## Current State
- Active. Created by Heartbeat-0.

## Physical Evidence
- `layers/l2_brain/heartbeat/heartbeat_lifecycle_runtime.py`
- `.aiwg/reports/heartbeat_latest.json`

## Contract Invariants
- never recommends autonomous scaling if blocked
- decision is NEEDS_HUMAN_REVIEW or repair_planning when Kuzu persistence is DEGRADED and action is repair_kuzu
- decision cannot be PASS if quality gate fails
- outputs valid JSON parsed under heartbeat_lifecycle schema

## Verification
```bash
pytest layers/l2_brain/tests/test_heartbeat_lifecycle_runtime.py
```

## Traceability
- HEARTBEAT-0 Module 1
