# Spec 83: Token Cost Ledger

## Goal
Provide a persistent, append-only record of cognitive costs (tokens) consumed by the DUMMIE Engine, categorized by session, mission, and phase.

## Storage
- Mission-specific: `.aiwg/missions/{mission_id}/token_cost_ledger.jsonl`
- Session-specific: `.aiwg/sessions/{session_id}/token_cost_ledger.jsonl`

## Core Requirements
- JSONL append-only format.
- Advisory file locking for concurrent writes.
- Idempotency via `event_id`.
- Support for multiple model tiers and providers.
- Summarization capabilities (mission, session, phase).
- Cache hit ratio calculation.
- Cloud cost estimation (placeholders for now).
- Protection against path traversal and private reasoning.
