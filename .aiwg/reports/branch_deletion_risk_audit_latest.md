# Branch Deletion Risk Audit

**Date:** 2026-05-19

## Local Branches

| Branch | HEAD | Unique Commits vs Main | Recommendation | Safe to Delete? |
|--------|------|----------------------|----------------|-----------------|
| intento-de-registrar-todo-con-arquitectura-y-estructura-canon | b78f3cd | 2 | KEEP | NO |
| hardening/structural-pack-2.2-polyglot-binding | f0345c8 | 0 (merged) | KEEP | NO |
| hardening/pack-3.1-reranker-hybrid-plus | 1efe580 | 0 (merged) | KEEP | NO |
| hardening/structural-pack-2 | f014d19 | 0 (merged) | KEEP | NO |
| hardening/structural-pack-2.1-critical-binding | eeaecf6 | 0 (merged) | KEEP | NO |
| hardening/structural-pack-2.3-batch-5-shellcheck | 06478a1 | 0 (merged) | KEEP | NO |
| hardening/structural-pack-2.4-superficial-tests | 1740db5 | 0 (merged) | KEEP | NO |
| main | 41e093f | 0 | KEEP | NEVER |
| backup/before-deletion-audit-20260519-065706 | b78f3cd | 0 | KEEP | NO |

## Critical Finding

The `hardening/structural-pack-2.2-polyglot-binding` branch shows ~100 deleted files vs main, including:
- All `dummie/` Python SDK files (`__init__.py`, `cli.py`, `engine.py`, etc.)
- All `.aiwg/identity/` config files
- All `.aiwg/state/` files
- Many test files
- Many script files

**However**, these deletions were part of the merge into main. The files were reorganized, not permanently lost. The branch reflects the state before merge.

## Global Rule

**NO branch is safe to delete during this audit.** All branches must be kept for review until the user explicitly approves deletion.
