# Folder Note: evolution

## Status
active

## Folder Path
`.aiwg/evolution`

## Purpose
phase state and roadmap source

## Canonical Sources
- `.aiwg/evolution`
- `.aiwg/world_model/project_world_model.json`
- `.aiwg/reports/spec_coverage_matrix.json`

## Linked Specs
- `doc/specs/104_plan_v1_cognitive_evolution_operating_layer.md`
- `doc/specs/106_agent_session_operating_contracts.md`
- `doc/specs/110_project_world_model.md`

## Linked Tests
- `scripts/validate_specs_docs.py`

## Linked Capabilities
- `PhaseLedger`


## Layer / Language Context
- Layer: `L0-L6`
- Languages: JSON, YAML, Markdown

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
