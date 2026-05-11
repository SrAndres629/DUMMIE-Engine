---
spec_id: "SPEC-76"
title: "Knowledge Vault"
status: "ACTIVE"
layer: "l2_brain"
governance: "crystallization"
last_verified_on: "2026-05-11"
---
# SPEC-76: Knowledge Vault

## Purpose
Define the mechanism for promoting successful mission artifacts from the temporary workbench to long-term crystalline memory (the Vault).

## Current State
Phase 4 of the Master Refactor. Establishing the transition from temporary execution traces to reusable knowledge patterns.

## Physical Evidence
- `layers/l2_brain/vault_curator.py`
- `.aiwg/vault/`
- `.aiwg/schemas/vault_entry.schema.json`

## Contract Invariants
- Only verified artifacts (from successful outcomes) SHOULD be promovoted to the Vault.
- Vault entries MUST be unique and tagged with mission origin.
- Sensitive or private data MUST be stripped before promotion.
- Each entry MUST include "reuse conditions" to guide future retrieval.

## Anatomical Components

### 4.1 VaultCurator
The logic engine that promotion:
- `extract_vault_entries`: Scans a finalized workbench for promotive candidates.
- `store_vault_entry`: Commits a candidate to the `.aiwg/vault/` directory.
- `finalize_and_clean`: Finalizes promotion and archives the workbench.

## Verification
- Unit tests: `layers/l2_brain/tests/test_vault_curator.py`
- Evidence: Indexed JSON files in `.aiwg/vault/`.

## Traceability
- Extends: SPEC-75 (Mission Workbench)
- Feeds: SPEC-02 (Memory Engine 4D-TES)
