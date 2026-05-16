---
spec_id: "126_mission_coherence_guard"
title: "126 Mission Coherence Guard"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "operationalization_pack_1"
last_verified_on: "2026-05-16"
---

# Spec 126: Mission Coherence Guard

## Purpose
Detect and prevent "latest artifact drift" in mission planning and orchestration by ensuring all generated mission files are coherent with the canonical roadmap state.

## Scope
- Canonical State: `current_position.json`, `next_phase_seed.json`.
- Tracked Artifacts: `mission_plan_latest.json`, `mission_orchestrator_dag_latest.json`, `next_executable_node_latest.json`.

## Runtime Behavior
1. Read canonical next_phase and construct the expected mission_id.
2. Inspect tracked artifacts for their mission_id and next_phase fields.
3. Compare them to canonical truth.
4. Detect heuristic risks like invented test paths in the DAG.
5. Produce `MissionCoherenceReport` with a final decision (PASS|FAIL).

## Safety Rules
- Report only; do not auto-regenerate unless explicitly called via the planner.
- Read-only access to evolution files.

## Relationship to P25.1
This guard was introduced in P25.1 specifically to address the risk of "living in MISSION_P23 while roadmap is at P26".

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
