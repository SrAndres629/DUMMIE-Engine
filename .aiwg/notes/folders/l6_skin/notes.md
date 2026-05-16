# Folder Note: l6_skin

## Status
active

## Folder Path
`layers/l6_skin`

## Purpose
UI/skin layer

## Canonical Sources
- `layers/l6_skin`
- `.aiwg/world_model/project_world_model.json`
- `.aiwg/reports/spec_coverage_matrix.json`

## Linked Specs
- `doc/specs/L6_Skin/13_observability_opentelemetry.md`
- `doc/specs/109_polyglot_architecture_registry.md`

## Linked Tests
- `layers/l6_skin/node_modules/@types/node/test/reporters.d.ts`

## Linked Capabilities
- capability linkage deferred or indirect


## Layer / Language Context
- Layer: `L6`
- Languages: Python, TypeScript, JavaScript

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
- TypeScript/JavaScript evidence is dominated by node_modules dependency files in current tracked scan.


## Refresh Triggers
- source_file_changed
- linked_spec_changed
- linked_test_failed
- coverage_matrix_changed

## Next Actions
- Recompute source hash in P10 freshness ledger.
- Expand test/spec linkage depth where confidence is medium or low.
- Promote to retrieval_candidate only when fresh and task-relevant.
