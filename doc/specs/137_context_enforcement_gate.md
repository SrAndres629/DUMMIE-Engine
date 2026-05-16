---
spec_id: "137_context_enforcement_gate"
title: "137 Context Enforcement Gate"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "operationalization_pack_1"
last_verified_on: "2026-05-16"
---

# Spec 137: Context Enforcement Gate

## Purpose
Enforce a context economy policy by prioritizing dossiers and manifests over raw file or folder reads.

## Scope
- Evaluates context requests based on user intent and task type.
- Blocks bulk raw folder scans.
- Recommends the most efficient context strategy (manifest-only, dossier, or selected read).

## Runtime Behavior
1. Receive a context request.
2. Check for repo intelligence manifest existence.
3. Apply blocking rules for raw bulk scans.
4. Return an `ALLOW_*` or `BLOCK_*` decision.

## Safety Rules
- Must block raw folder bulk loads if folder dossiers exist.
- Manifest context is preferred for planning tasks.


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
