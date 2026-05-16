# Folder Note: l4_edge

## Status
active

## Folder Path
`layers/l4_edge`

## Purpose
edge/adapters/sensors layer

## Canonical Sources
- `layers/l4_edge`
- `.aiwg/world_model/project_world_model.json`
- `.aiwg/reports/spec_coverage_matrix.json`

## Linked Specs
- `doc/specs/L4_Edge/18_loci_ontology_mapping.md`
- `doc/specs/109_polyglot_architecture_registry.md`

## Linked Tests
- none discovered in this phase

## Linked Capabilities
- capability linkage deferred or indirect


## Layer / Language Context
- Layer: `L4`
- Languages: Python, Zig

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
