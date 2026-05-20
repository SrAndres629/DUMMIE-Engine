# Deletion Incident Report — Final

**Date:** 2026-05-19
**Incident:** Deletion + Flat L2 Reorganization Risk
**Decision:** FAIL

## Executive Summary

The audit found **zero locally deleted files** in the working tree. All deletions exist in committed history. The `flat_brain` migration on the current branch moved ~180+ files from `layers/l2_brain/*` to `layers/l2_brain/flat_brain/*` without a manifest, dry-run, or rollback plan. This migration broke spec-to-code traceability for 58+ spec documents.

## Decision: FAIL

The audit returns **FAIL** because:
1. Source/spec files deleted in committed history have not been restored
2. 58+ spec documents have broken file path references
3. Flat L2 migration executed without manifest/dry-run/rollback
4. Downstream imports to old `l2_brain` paths will break

## Key Numbers

| Metric | Value |
|--------|-------|
| Local deleted files | 0 |
| Committed deletion entries (30 commits) | 3,371 |
| Files moved in flat_brain migration | ~180+ |
| Spec docs with broken paths | 58+ |
| Files recommended for restore | 5 |
| Files actually restored | 0 |
| Branches safe to delete | 0 |
| Branches to keep | 9 |

## Critical Findings

### 1. No Local Deletions
Working tree has no deleted tracked files. All changes are modifications.

### 2. Flat L2 Migration (CRITICAL)
Commits `3539c7e` and `b78f3cd` moved ~180+ files into `layers/l2_brain/flat_brain/`.
- No migration manifest
- No dry-run evidence
- No rollback plan
- Broke 58+ spec document references
- pattern_miner.py was modified during move (D+A, not R)

### 3. Committed Deletions Requiring Review
- `.aiwg/memory/lessons.jsonl` — Sovereign memory file, should be restored
- `mcp_server.py` + `test_mcp_server.py` — Source/test code, verify migration
- `ports.py` + `schemas.py` — Source code, verify migration to models.py

### 4. Spec Validation Failure
All spec documents referencing `layers/l2_brain/X.py` fail validation because files moved to `layers/l2_brain/flat_brain/X.py`.

## Files Created (Audit Reports)

1. `.aiwg/reports/deletion_incident_reality_lock_latest.json`
2. `.aiwg/reports/deletion_incident_reality_lock_latest.md`
3. `.aiwg/reports/deleted_files_local_raw.txt`
4. `.aiwg/reports/deleted_files_local_latest.json`
5. `.aiwg/reports/deleted_files_local_latest.md`
6. `.aiwg/reports/deleted_files_recent_commits_raw.txt`
7. `.aiwg/reports/recent_branches_and_commits_raw.txt`
8. `.aiwg/reports/deleted_files_recent_commits_latest.json`
9. `.aiwg/reports/deleted_files_recent_commits_latest.md`
10. `.aiwg/reports/last_known_good_candidate_latest.json`
11. `.aiwg/reports/branch_deletion_risk_audit_latest.json`
12. `.aiwg/reports/branch_deletion_risk_audit_latest.md`
13. `.aiwg/reports/flat_l2_incident_analysis_latest.json`
14. `.aiwg/reports/flat_l2_incident_analysis_latest.md`
15. `.aiwg/reports/deletion_restore_plan_latest.json`
16. `.aiwg/reports/deletion_restore_plan_latest.md`
17. `.aiwg/reports/deletion_incident_validation_latest.json`
18. `.aiwg/reports/deletion_incident_validation_latest.md`
19. `.aiwg/reports/deletion_incident_report_latest.json`
20. `.aiwg/reports/deletion_incident_report_latest.md`

## Recommendation

1. **IMMEDIATE:** Restore `.aiwg/memory/lessons.jsonl` from commit `f3485dc^`
2. **REVIEW:** Check if `mcp_server.py`, `ports.py`, `schemas.py` functionality was migrated
3. **DECIDE:** Keep or revert the `flat_brain` migration
   - If KEEP: Update all 58+ spec document paths
   - If REVERT: Reset to `41e093f` (main HEAD)
4. **DEFER:** No branch deletions until this audit is reviewed
5. **DEFER:** No further structural refactoring until migration is validated

## Next Safe Action

Review this report. Decide on restore and migration strategy. Do NOT proceed with any destructive operation until reviewed.
