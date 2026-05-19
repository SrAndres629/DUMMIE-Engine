# PACK R2.1 Input Summary

**Source Reports:**
- `deletion_incident_report_latest.json` — Decision: FAIL, 5 files recommended for restore
- `deletion_restore_plan_latest.json` — Restore commands for 5 files
- `flat_l2_incident_analysis_latest.json` — ~180+ files migrated, 58+ specs broken
- `deletion_incident_validation_latest.json` — Spec validation FAIL (58 broken)
- `deleted_files_recent_commits_latest.json` — 3371 committed deletion entries

## Restore Candidates

| File | Source Commit | Risk | Status |
|------|--------------|------|--------|
| `.aiwg/memory/lessons.jsonl` | f3485dc^ | LOW | RESTORED |
| `layers/l2_brain/src/brain/mcp_server.py` | f3485dc^ | MEDIUM | RESTORED |
| `layers/l2_brain/tests/test_mcp_server.py` | f3485dc^ | MEDIUM | RESTORED |
| `layers/l2_brain/src/brain/application/ports.py` | 762eec1^ | MEDIUM | RESTORED |
| `layers/l2_brain/src/brain/domain/memory/schemas.py` | 762eec1^ | MEDIUM | RESTORED |

## Broken Specs

58 spec docs referencing `layers/l2_brain/X.py` — all files exist at `layers/l2_brain/flat_brain/X.py`.

## Flat Brain Migration

235 files migrated in commits 3539c7e and b78f3cd.
Last known good commit: 41e093f (main HEAD).
