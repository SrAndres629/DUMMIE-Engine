---
spec_id: 138_repo_intelligence_query
title: 138 Repo Intelligence Query
status: ACTIVE
canonicality: canonical
artifact_type: spec
plan: DUMMIE PLAN V1
layer: l2_brain
created_by: operationalization_pack_1
last_verified_on: '2026-05-16'
claims:
- id: 138_repo_intelligence_query-file-valid
  description: Spec file '138_repo_intelligence_query.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/138_repo_intelligence_query.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
# Spec 138: Repo Intelligence Query

## Purpose
Provide a deterministic, code-based interface to query the repository's physical state without reading files directly.

## Scope
- Filtering by layer, language, artifact type, and technical debt category.
- Finding untested runtime modules.
- Determining context strategy for specific paths.

## Runtime Behavior
1. Read the `repo_inventory.json`.
2. Apply filter parameters.
3. Return a list of matching file facts.

## Safety Rules
- Must not read the contents of files, only inventory metadata.


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
