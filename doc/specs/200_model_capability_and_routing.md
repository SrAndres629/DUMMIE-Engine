---
spec_id: "DE-V2-L2-200"
title: "Model Capability and Routing Engine"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-24"
---

## Purpose
To provide a canonical registry of AI model capabilities and a deterministic routing logic to select the most appropriate model based on task intent, cost, and latency.

## Current State
Implemented during Pack 4.0 and 4.1. Includes a central registry and a routing service integrated into the Cognitive Orchestrator.

## Physical Evidence
- Core Registry: `layers/l2_brain/src/brain/domain/capability_registry.py`
- Routing Service: `layers/l2_brain/src/brain/application/services/model_router.py`
- Integration: `layers/l2_brain/src/brain/application/use_cases/orchestrator.py`
- Test Suite: `layers/l2_brain/tests/test_capability_registry.py`, `layers/l2_brain/tests/test_model_router_v2.py`

## Contract Invariants
- **Registry Uniqueness**: Model capabilities are unique by `model_id`.
- **Expertise Alignment**: Routing must prioritize models with the matching `ModelExpertise` for a given `IntentType`.
- **Fallback Safety**: If no specialist model is found, the system must fallback to a designated `default_model`.
- **Cost-Latency Optimization**: When multiple candidates exist, selection prioritizes lower cost and lower latency score.

## Verification
Run tests via pytest:
```bash
. .venv/bin/activate && PYTHONPATH=layers/l2_brain/src pytest -v layers/l2_brain/tests/test_capability_registry.py layers/l2_brain/tests/test_model_router_v2.py
```

## Traceability
- Maps to: `PACK_4.0`, `PACK_4.1` in `pack_roadmap_to_6_1.json`.
- Internal reference: `DE-V2-L2-200`.
