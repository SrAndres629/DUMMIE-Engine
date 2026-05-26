---
spec_id: 123_repo_probe_runner
title: 123 Repo Probe Runner
status: ACTIVE
canonicality: canonical
artifact_type: spec
plan: DUMMIE PLAN V1
layer: l2_brain
created_by: operationalization_pack_1
last_verified_on: '2026-05-16'
claims:
- id: 123_repo_probe_runner-file-valid
  description: Spec file '123_repo_probe_runner.md' exists, parses valid YAML frontmatter,
    and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/123_repo_probe_runner.md').read().split('---')[1]); assert d,
    'empty frontmatter'"
  severity: critical
---
# Spec 123: Repo Probe Runner

## Purpose
Ground the DUMMIE engine's world model in physical evidence by deterministic inspection of the repository structure, layers, languages, specs, and tests.

## Scope
- Layer inspection (L0-L6).
- Polyglot language mapping.
- Spec triplet validation (.md, .feature, .rules.json).
- Critical runtime module presence.
- State coherence guard integration.

## Runtime Behavior
1. Use `git ls-files` to gather a list of all tracked files.
2. Analyze file paths to determine layer presence and language distribution.
3. Check for the existence of critical files in `layers/l2_brain/`.
4. Validate that each spec in `doc/specs/` has its corresponding `.feature` and `.rules.json`.
5. Read the latest `state_coherence_guard` report to ensure local consistency.
6. Produce `repo_probe_latest.json`.

## Safety Rules
- Do not read entire file contents; use metadata and path analysis.
- Do not include secrets or API keys in evidence.
- Do not modify any files.

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
