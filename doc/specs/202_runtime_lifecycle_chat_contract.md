---
spec_id: "DE-V2-L2-202"
title: "Runtime Lifecycle Chat Contract"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-19"
---

## Purpose
Define the canonical contract for `dummie chat` as a runtime/lifecycle orchestration flow instead of a direct single-model chat.

## Current State
Implemented in `dummie/runtime_chat.py` and integrated into `DummieEngine.chat(...)`, with deterministic preprocessing, model tier routing, provider selection, and traceability receipts.

## Physical Evidence
- Runtime contract: `dummie/runtime_chat.py`
- Engine integration test: `tests/test_dummie_engine.py`
- CLI integration test: `tests/test_dummie_cli.py`
- Runtime report: `.aiwg/reports/runtime_chat_latest.json`
- Runtime trace report: `.aiwg/reports/runtime_chat_trace_latest.json`
- Runtime registry: `.aiwg/runtime/runtime_chat_registry.yaml`
- Spec contract: `doc/specs/202_runtime_lifecycle_chat_contract.md`
- Spec scenario: `doc/specs/202_runtime_lifecycle_chat_contract.feature`
- Spec rules: `doc/specs/202_runtime_lifecycle_chat_contract.rules.json`

## Contract Invariants
- `dummie chat` must run preprocessing and routing before lifecycle response.
- Runtime mode is `runtime_lifecycle_orchestration`, configured by one registry file.
- Each chat call writes a report, a trace report, and a receipt.
- Low-cost mode must avoid cloud-first behavior and keep deterministic preprocessing enabled.

## Verification
```bash
uv run pytest -q tests/test_dummie_engine.py tests/test_dummie_cli.py
python3 scripts/validate_specs_docs.py --check doc/specs/202_runtime_lifecycle_chat_contract.md
```

## Traceability
- Pack lineage: `PACK_S1` CLI sovereignty hardening.
- Depends on: `doc/specs/200_model_capability_and_routing.md`.
- Related capability: centralized runtime/provider orchestration across local and cloud backends.
