---
spec_id: 128_debate_review_runtime
title: 128 Debate Review Runtime
status: ACTIVE
canonicality: canonical
artifact_type: spec
plan: DUMMIE PLAN V1
layer: l2_brain
created_by: operationalization_pack_1
last_verified_on: '2026-05-16'
claims:
- id: 128_debate_review_runtime-file-valid
  description: Spec file '128_debate_review_runtime.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/128_debate_review_runtime.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
# Spec 128: Debate & Adversarial Review Runtime

## Purpose
Prevent consensus bias and identify planning flaws by forcing a structured debate between specialized roles before any mission execution.

## Scope
- Roles: proposer, skeptic, evidence_auditor, risk_challenger, implementation_reviewer, mentor_judge.
- Detection: missing evidence, coherence failures, consensus bias, unsafe autonomy requests.

## Runtime Behavior
1. Gather reports from previous phases (Repo Probe, Mission Plan, Swarm, Coherence).
2. Execute deterministic adversarial reasoning for each role.
3. Proposer claims readiness; Skeptic challenges with consensus bias checks.
4. Auditor verifies physical evidence grounding.
5. Reviewer checks SDD/TDD compliance (e.g., missing test paths).
6. Mentor Judge issues a final verdict (accept|repair|block).

## Safety Rules
- Advisory-only: no workspace mutation.
- Must block if MissionCoherenceGuard failed.
- Must flag if a plan for a runtime module has no tests.

## Relationship to P26
Consumes StrategicPartnerSwarm outputs to challenge their consensus.

## Current State
- TBD

## Physical Evidence
- TBD

## Contract Invariants
- TBD

## Verification
- TBD

## Traceability
- TBD
