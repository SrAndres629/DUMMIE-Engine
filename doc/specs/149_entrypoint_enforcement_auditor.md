---
spec_id: 149_entrypoint_enforcement_auditor
title: 149 Entrypoint Enforcement Auditor
status: ACTIVE
canonicality: canonical
artifact_type: spec
plan: DUMMIE PLAN V1
layer: l2_brain
created_by: operationalization_pack_3
last_verified_on: '2026-05-16'
claims:
- id: 149_entrypoint_enforcement_auditor-file-valid
  description: Spec file '149_entrypoint_enforcement_auditor.md' exists, parses valid
    YAML frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/149_entrypoint_enforcement_auditor.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# Spec 149: Entrypoint Enforcement Auditor

## Purpose
Audit all sovereign entrypoints to detect which ones bypass context gate, skip memory spine, or fail to record outcomes and token costs.

## Scope
- Audits 8 named entrypoints by static source analysis.
- Detects missing context gate, repo intelligence, outcome recording, token cost, memory spine, report writing, and CLI exposure.
- Reports PASS_WITH_WARNINGS when entrypoints have gaps (not FAIL, since integration is progressive).

## Runtime Behavior
1. Enumerate all known entrypoint module paths.
2. Read source code and check for key integration patterns.
3. Generate EntrypointEnforcementAudit per entrypoint.
4. Write JSON and MD reports.

## Safety Rules
- Report-only. Does not mutate workspace.
- Must not fail because entrypoints lack some integrations — report warnings instead.

## Current State
- Operational. Detects missing integrations across 8 entrypoints.

## Physical Evidence
- `layers/l2_brain/governance/entrypoint_enforcement_auditor.py`
- `.aiwg/reports/entrypoint_enforcement_audit_latest.json`
- `.aiwg/schemas/entrypoint_enforcement_audit.schema.json`

## Contract Invariants
- Must audit at least 8 entrypoints.
- Must never crash due to missing entrypoint files.
- Decision must be PASS or PASS_WITH_WARNINGS (never FAIL for missing integrations).

## Verification
```bash
python3 layers/l2_brain/governance/entrypoint_enforcement_auditor.py
python3 -m pytest layers/l2_brain/tests/test_entrypoint_enforcement_auditor.py -q
```

## Traceability
- Implements POST_PLAN_V1_OPERATIONALIZATION_PACK_3 Module 4.
- Consumed by readiness calibrator and sovereign runtime readiness.
