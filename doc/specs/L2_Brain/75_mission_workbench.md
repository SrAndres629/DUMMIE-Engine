---
spec_id: SPEC-75
title: Mission Workbench
status: ACTIVE
layer: L2
governance: persistence
last_verified_on: '2026-05-11'
version: 1.0.0
namespace: dummie.engine.l2_brain
claims:
- id: 75_mission_workbench-file-valid
  description: Spec file '75_mission_workbench.md' exists, parses valid YAML frontmatter,
    and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/L2_Brain/75_mission_workbench.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
# SPEC-75: Mission Workbench

## Purpose
Establish a physical, persistent workspace for every mission to store reasoning artifacts, execution evidence, and outcome metrics.

## Current State
Phase 3 of the Master Refactor. Replacing transient memory with structured filesystem artifacts.

## Physical Evidence
- `layers/l2_brain/mission_workbench.py`
- `layers/l2_brain/tests/test_mission_workbench.py`
- `.aiwg/schemas/mission_workbench.schema.json`

## Runtime Paths
- `.aiwg/workbench/{mission_id}/` is created per mission at runtime and must not be treated as static Physical Evidence.

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
- Runtime checkpoint: presence of structured artifacts after a mission execution.

## Traceability
- Extends: SPEC-73 (Cognitive Body Architecture)
- Pre-requisite for: SPEC-76 (Knowledge Vault)
