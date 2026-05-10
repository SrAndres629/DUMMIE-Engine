# Event Protocol

## Purpose
Define auditable repo and session events for DUMMIE self-evolution.

## Agent
Cartographer and SelfWorktreeOrchestrator produce events; Validator consumes them.

## Format
Events are JSONL records with `event_id`, `timestamp`, `event_type`, `path` or `summary`, evidence refs, and `six_d_context`.

## Allowed
- FILE_ADDED
- FILE_MODIFIED
- FILE_DELETED
- FILE_HASH_CHANGED
- INTAKE
- GLOBAL_RECALL
- EPISTEMIC_CHECK
- PATCH_PLAN
- VALIDATION
- NEXT_LOOP

## Prohibited
- Events without timestamps.
- Events that claim success without verification evidence.

## Validation
Run `python3 scripts/watch_repo_events.py --root . --once --dry-run` before writing watcher state.

## 4D-TES / 6D Connection
Each event should carry locus, Lamport time, authority, and intent when the producer has that context.
