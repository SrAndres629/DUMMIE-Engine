---
spec_id: SPEC-74
title: Runtime Token Economy
status: ACTIVE
layer: L2
governance: metabolism
last_verified_on: '2026-05-11'
version: 1.0.0
namespace: dummie.engine.l2_brain
claims:
- id: 74_runtime_token_economy-file-valid
  description: Spec file '74_runtime_token_economy.md' exists, parses valid YAML frontmatter,
    and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/L2_Brain/74_runtime_token_economy.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# SPEC-74: Runtime Token Economy

## Purpose
Establish a centralized, empirical accounting system for managing LLM token consumption and context budgets across the DUMMIE Engine.

## Current State
Partially implemented. Character-based estimation exists in `MetaGatewayRuntimeMeter`. Phase 2 will introduce the `TokenCostLedger` and `ContextBudgetManager`.

## Physical Evidence
- `layers/l2_brain/token_cost_ledger.py`
- `layers/l2_brain/context/context_budget_manager.py`
- `.aiwg/schemas/token_cost_ledger.schema.json`
- `.aiwg/schemas/context_budget.schema.json`

## Contract Invariants
- All token consumption events MUST be recorded in the `TokenCostLedger`.
- Budgets MUST be allocated per session/mission before invoking any model.
- The `ContextBudgetManager` MUST recommend compression or truncation when context pressure exceeds 80%.

## Architecture

### 2.1 TokenCostLedger
Records granular usage events:
- `input_tokens`, `output_tokens`, `cached_tokens`, `reasoning_tokens`.
- `model_tier`, `provider`, `mission_id`.

### 2.2 ContextBudgetManager
Governs context allocation:
- Allocates budgets based on priority and authority.
- Enforces limits to prevent cloud cost spikes.

## Verification
- Unit tests: `layers/l2_brain/tests/test_token_cost_ledger.py`
- Integration: `layers/l2_brain/tests/test_context_budget_manager.py`

## Traceability
- Extends: SPEC-73 (Cognitive Body Architecture)
- References: SPEC-40 (Token Optimization Protocol)
