# DUMMIE PLAN V1 - P9 FolderNotes + NotePlans

## Decision
PASS_WITH_WARNINGS

## Summary
P9 established governed tier-0 FolderNotes and NotePlans using world model and coverage matrix as canonical inputs, with source hashes and freshness triggers for future stale detection.

## Advanced Reasoning Summary
Claims:
- Folder-level compression is required to avoid repeated raw-folder scans.
- Notes must stay derived so they cannot override canonical truth sources.
- P10 needs deterministic hash/freshness hooks from P9 outputs.

Objections:
- Notes can become stale narrative debt if not hash-governed.
- Large folders (for example l0_overseer and specs) can hide dependency noise.
- Coverage links can drift if matrix changes are not tracked.

Decisions:
- Tier-0 scope only, no massive note explosion.
- Default token role `summary_only` across all folder notes.
- Manifest-level freshness and non-override policy enforced.

Risks:
- Freshness drift until P10 automates stale detection.
- Dependency-heavy folders may reduce note confidence.
- Spec legacy debt remains inherited and unresolved in this phase.

## Manifest Created
- `.aiwg/notes/folder_notes_manifest.json`

## Folder Notes Created
- 11 tier-0 folder notes under `.aiwg/notes/folders/*/notes.md`

## NotePlans Created
- 11 noteplans under `.aiwg/notes/folders/*/noteplan.md`

## Truth Policy
FolderNotes are derived artifacts and cannot override code, tests, specs, schemas, ledgers, world model, or current phase files.

## Freshness / Source Hash Policy
- hash method: `sha256(sorted_git_ls_files_plus_counts)`
- source hash tracked per folder
- refresh triggers include source/spec/test/coverage changes

## Token Role Policy
FolderNotes default to `summary_only` and may become `retrieval_candidate` only when fresh and task-relevant.

## Coverage Linkage
All notes link back to `.aiwg/reports/spec_coverage_matrix.json` through manifest policy and noteplan constraints.

## Path Missing / Low Confidence Notes
No required tier-0 folder path was missing in this run; dependency-heavy folders remain flagged with caution risks.

## Anti-Stale Narrative Debt Controls
- derived-only truth rank 40
- explicit non-override controls
- per-folder source hashes
- P10 handoff for stale detection automation

## What P10 Must Consume
- `.aiwg/notes/folder_notes_manifest.json`
- `.aiwg/schemas/folder_note.schema.json`
- `.aiwg/schemas/noteplan.schema.json`
- `.aiwg/reports/spec_coverage_matrix.json`
- `.aiwg/world_model/project_world_model.json`

## Known Warnings
- Inherited debt: `DEBT-SPEC-LEGACY-MCP-GUIDE` (`doc/guides/mcp_server_usage.md` references missing Specs 2, 7, 15, 35, 41, 42, 44).
- Freshness enforcement is policy-defined here but runtime enforcement is deferred to P10.

## Remaining Risks
- Folder-note freshness can drift before P10 checks run.
- Dependency-heavy paths can still bias summaries if not filtered in future phases.

## Next Phase
P10 - FreshnessLedger + StaleMemoryDetector
