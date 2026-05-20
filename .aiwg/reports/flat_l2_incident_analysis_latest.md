# Flat L2 Incident Analysis

**Date:** 2026-05-19

## Problem Confirmed: YES

The `flat L2 brain` issue triggered a massive reorganization of `layers/l2_brain/`.

## Current State of layers/l2_brain/

| Metric | Value |
|--------|-------|
| Top-level files (config only) | 7 |
| Files in flat_brain/ subdirectory | 582 (physical) / 237 (tracked) |
| Tracked files outside flat_brain/ | ~30 (src/brain/, .aiwg/, config) |
| Files deleted in current branch commits | 2 (pattern_miner.py, router.py) |
| Files renamed/moved in current branch commits | ~180+ |

## What Happened

Commits `3539c7e` and `b78f3cd` migrated ~180+ files from:
- `layers/l2_brain/action_graph.py` → `layers/l2_brain/flat_brain/action_graph.py`
- `layers/l2_brain/cognition/cold_planner.py` → `layers/l2_brain/flat_brain/cognition/cold_planner.py`
- `layers/l2_brain/embedding_mesh/*.py` → `layers/l2_brain/flat_brain/embedding_mesh/*.py`
- ... and ~177 more files

## Unsafe Refactor Signals

1. **No manifest** — No migration plan or manifest file documenting the move
2. **No dry-run** — No evidence of testing the migration before committing
3. **No rollback** — No rollback strategy documented
4. **D+A instead of R** — pattern_miner.py was deleted and re-added (not renamed), meaning it was modified during the move
5. **No import verification** — All downstream imports to old paths will break
6. **No test evidence** — No mention of test suite validation in commit messages

## Recommendation: RESTORE_FIRST

Before any further refactor:
1. Audit all import paths that reference `layers/l2_brain/*` modules
2. Verify that the flat_brain versions are functionally equivalent
3. Consider adding import compatibility shims for backward compatibility
4. Do NOT proceed with additional structural changes until this migration is validated
