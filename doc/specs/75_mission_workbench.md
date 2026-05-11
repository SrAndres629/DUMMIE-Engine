---
spec_id: "SPEC-75"
title: "Mission Workbench"
status: "ACTIVE"
layer: "l2_brain"
governance: "persistence"
last_verified_on: "2026-05-11"
---
# SPEC-75: Mission Workbench

## Purpose
Establish a physical, persistent workspace for every mission to store reasoning artifacts, execution evidence, and outcome metrics.

## Current State
Phase 3 of the Master Refactor. Replacing transient memory with structured filesystem artifacts.

## Physical Evidence
- `layers/l2_brain/mission_workbench.py`
- `.aiwg/workbench/{mission_id}/`
- `.aiwg/schemas/mission_workbench.schema.json`

## Contract Invariants
- Every mission MUST have a unique directory under `.aiwg/workbench/`.
- No secrets or private chain-of-thought artifacts MUST be stored in the workbench.
- Path traversal outside of `.aiwg/workbench/` MUST be blocked.
- Artifacts MUST be serializable to valid JSON, YAML, or Markdown.

## Anatomical Components

### 3.1 MissionWorkbenchManager
Handles the lifecycle of the workbench:
- `create_workbench`: Initializes the directory and base files.
- `write_artifact`: Saves specific files (objectives, graphs, logs).
- `append_decision`: Adds an entry to the `decision_log.jsonl`.
- `finalize_workbench`: Generates the final summary and learning episode link.

## Verification
- Unit tests: `layers/l2_brain/tests/test_mission_workbench.py`
- Checkpoint: Presence of structured artifacts after a mission execution.

## Traceability
- Extends: SPEC-73 (Cognitive Body Architecture)
- Pre-requisite for: SPEC-76 (Knowledge Vault)
