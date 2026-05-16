# Folder Note: l0_overseer

## Status
active

## Folder Path
`layers/l0_overseer`

## Purpose
overseer/orchestration layer

## Canonical Sources
- `layers/l0_overseer`
- `.aiwg/world_model/project_world_model.json`
- `.aiwg/reports/spec_coverage_matrix.json`

## Linked Specs
- `doc/specs/L0_Overseer/03_polyglot_architecture.md`
- `doc/specs/109_polyglot_architecture_registry.md`

## Linked Tests
- `layers/l0_overseer/cmd/dummied/main_test.go`
- `layers/l0_overseer/internal/orchestrator/integrity_test.go`
- `layers/l0_overseer/internal/orchestrator/security_test.go`
- `layers/l0_overseer/internal/orchestrator/socket_path_test.go`
- `layers/l0_overseer/test/overseer_ipc_test.exs`
- `layers/l0_overseer/test/test_helper.exs`

## Linked Capabilities
- capability linkage deferred or indirect


## Layer / Language Context
- Layer: `L0`
- Languages: Go, Elixir, Python

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
- Tracked deps/_build content can inflate language perception without first-party filtering.


## Refresh Triggers
- source_file_changed
- linked_spec_changed
- linked_test_failed
- coverage_matrix_changed

## Next Actions
- Recompute source hash in P10 freshness ledger.
- Expand test/spec linkage depth where confidence is medium or low.
- Promote to retrieval_candidate only when fresh and task-relevant.
