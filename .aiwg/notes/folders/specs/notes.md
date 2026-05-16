# Folder Note: specs

## Status
active

## Folder Path
`doc/specs`

## Purpose
SDD contract source

## Canonical Sources
- `doc/specs`
- `.aiwg/world_model/project_world_model.json`
- `.aiwg/reports/spec_coverage_matrix.json`

## Linked Specs
- `doc/specs/107_cognitive_artifact_protocol.md`
- `doc/specs/108_truth_hierarchy_canonicality_policy.md`
- `doc/specs/109_polyglot_architecture_registry.md`
- `doc/specs/110_project_world_model.md`
- `doc/specs/111_spec_coverage_gate.md`

## Linked Tests
- `scripts/validate_specs_docs.py`

## Linked Capabilities
- `CognitiveHooks`


## Layer / Language Context
- Layer: `L0-L6`
- Languages: Markdown, Gherkin, JSON

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
- Large specification surface can drift without coverage gating.


## Refresh Triggers
- source_file_changed
- linked_spec_changed
- linked_test_failed
- coverage_matrix_changed

## Next Actions
- Recompute source hash in P10 freshness ledger.
- Expand test/spec linkage depth where confidence is medium or low.
- Promote to retrieval_candidate only when fresh and task-relevant.
