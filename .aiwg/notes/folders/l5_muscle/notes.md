# Folder Note: l5_muscle

## Status
active

## Folder Path
`layers/l5_muscle`

## Purpose
execution/muscle layer

## Canonical Sources
- `layers/l5_muscle`
- `.aiwg/world_model/project_world_model.json`
- `.aiwg/reports/spec_coverage_matrix.json`

## Linked Specs
- `doc/specs/L5_Muscle/01_environment_and_hardware.md`
- `doc/specs/109_polyglot_architecture_registry.md`

## Linked Tests
- `layers/l5_muscle/tests/test_workstation_operator.py`

## Linked Capabilities
- capability linkage deferred or indirect


## Layer / Language Context
- Layer: `L5`
- Languages: Python, Mojo

## Truth Policy
- This note is derived, not canonical.
- Code/tests/specs outrank this note.
- This note must be refreshed when source_hash changes.

## Token Role
summary_only

## What To Load Instead Of Raw Folder
- `.aiwg/notes/folder_notes_manifest.json`
- `.aiwg/world_model/project_world_model.json`
- This folder note and its noteplan.

## Risks
- Potential freshness drift if source files change and note is not refreshed.


## Refresh Triggers
- source_file_changed
- linked_spec_changed
- linked_test_failed
- coverage_matrix_changed

## Next Actions
- Recompute source hash in P10 freshness ledger.
- Expand test/spec linkage depth where confidence is medium or low.
- Promote to retrieval_candidate only when fresh and task-relevant.
