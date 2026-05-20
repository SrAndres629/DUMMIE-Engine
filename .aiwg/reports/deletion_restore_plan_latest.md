# Deletion Restore Plan

**Date:** 2026-05-19

## Local Working Tree: NO restores needed

No tracked files are deleted in the working tree.

## Committed Deletions: 5 files recommended for review/restore

### HIGH PRIORITY — Restore Recommended

| # | File | Source Commit | Risk | Command |
|---|------|--------------|------|---------|
| 1 | `.aiwg/memory/lessons.jsonl` | f3485dc^ | LOW | `git show f3485dc^:.aiwg/memory/lessons.jsonl > .aiwg/memory/lessons.jsonl` |

**Reason:** Sovereign memory file. Critical for DUMMIE continuity. Should not have been deleted.

### MEDIUM PRIORITY — Review Before Restore

| # | File | Source Commit | Risk | Command |
|---|------|--------------|------|---------|
| 2 | `layers/l2_brain/src/brain/mcp_server.py` | f3485dc^ | MEDIUM | `git show f3485dc^:layers/l2_brain/src/brain/mcp_server.py > /tmp/mcp_server_deleted.py` |
| 3 | `layers/l2_brain/tests/test_mcp_server.py` | f3485dc^ | MEDIUM | `git show f3485dc^:layers/l2_brain/tests/test_mcp_server.py > /tmp/test_mcp_server_deleted.py` |
| 4 | `layers/l2_brain/src/brain/application/ports.py` | 762eec1^ | MEDIUM | `git show 762eec1^:layers/l2_brain/src/brain/application/ports.py > /tmp/ports_deleted.py` |
| 5 | `layers/l2_brain/src/brain/domain/memory/schemas.py` | 762eec1^ | MEDIUM | `git show 762eec1^:layers/l2_brain/src/brain/domain/memory/schemas.py > /tmp/schemas_deleted.py` |

**Reason:** Source/test code. Verify if functionality was migrated to flat_brain/ or new contract modules before restoring.

### NOT Recommended for Restore

- `.aiwg/reports/*_latest.*` — Generated reports (~200+ files)
- `__pycache__/*.pyc` — Python cache
- `*.pb.go`, `*.pb.ex` — Generated protobuf
- `bin/l1_nervous`, `layers/l3_shield/target` — Build artifacts
- `doc/01_architecture/adr/0010-l2-infrastructure-bridge.md` — Superseded ADR

## Execution Rule

**DO NOT execute any restore without explicit user approval.**
First review the deleted file contents with `git show <commit>:<path>` to determine if they are still needed.
