---
spec_id: "133_repo_intelligence_runtime"
title: "133 Repo Intelligence Runtime"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "operationalization_pack_1"
last_verified_on: "2026-05-16"
---

# Spec 133: Repo Intelligence Runtime

## Purpose
Perform a physical, deterministic inventory of the repository to classify files and directories by architectural layer, language, and artifact type without invoking LLMs for bulk reading.

## Scope
- Tracks all files via `git ls-files`.
- Classifies files as runtime, spec, schema, test, report, generated, or dependency.
- Produces a deterministic manifest and detailed inventory.

## Runtime Behavior
1. Run `git ls-files` to gather tracked paths.
2. Apply heuristic path and extension matching.
3. Skip reading content for generated or large vendor files.
4. Output `.aiwg/repo_intelligence/repo_inventory.json` and manifest.

## Safety Rules
- Must not load entire repo contents into memory.
- Must not invoke external APIs or LLMs.

## Relationship to context economy
Provides the foundation for contextual filtering, ensuring DUMMIE only loads necessary parts of the codebase.

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
