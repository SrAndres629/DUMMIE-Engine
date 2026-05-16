---
spec_id: "DE-V2-L2-105"
title: "Mental Model Abstraction Layer"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
version: "1.0.0"
namespace: "dummie.engine.plan_v1"
---
# Spec 105 - Mental Model Abstraction Layer

## Purpose

DUMMIE must operate through canonical mental models that transform temporal context into governed cognitive state.

## Current State

Implemented as Phase 1 mental model artifacts under `.aiwg/mental_models/` and context transform artifacts under `.aiwg/context_transform/`. The layer defines operating contracts and parseable state; it does not implement heavy ContextQuant runtime.

## Physical Evidence

- `.aiwg/mental_models/mental_model_registry.yaml`
- `.aiwg/mental_models/context_laplace_transform.md`
- `.aiwg/mental_models/context_state_space.json`
- `.aiwg/mental_models/cognitive_operating_principles.md`
- `.aiwg/context_transform/context_transform_manifest.yaml`
- `.aiwg/context_transform/context_transform_receipt.schema.json`
- `.aiwg/context_transform/per_message_operating_contract.yaml`

## Requirements

- Mental model registry exists at `.aiwg/mental_models/mental_model_registry.yaml`.
- Context transform documentation exists at `.aiwg/mental_models/context_laplace_transform.md`.
- Context state space exists at `.aiwg/mental_models/context_state_space.json`.
- Cognitive operating principles exist at `.aiwg/mental_models/cognitive_operating_principles.md`.
- The Laplace metaphor is operational and explicitly not a real mathematical computation.

## Contract Invariants

- The context transform metaphor must not be represented as real mathematics.
- Temporal context is converted into governed cognitive state.
- Private chain-of-thought and secrets are forbidden transform inputs.
- Engine-native integration is a canonical mental model.
- Deferred capability is not treated as permanent prohibition.

## Verification

```bash
python3 scripts/validate_specs_docs.py --check doc/specs/105_mental_model_abstraction_layer.md
python3 - <<'PY'
import json
from pathlib import Path
import yaml
assert yaml.safe_load(Path('.aiwg/mental_models/mental_model_registry.yaml').read_text())['mental_models']
state = json.loads(Path('.aiwg/mental_models/context_state_space.json').read_text())
assert 'objective_state' in state['states']
assert 'session_state' in state['states']
PY
```

## Traceability

| Invariant | Evidence | Verification |
| --- | --- | --- |
| Registry exists | `.aiwg/mental_models/mental_model_registry.yaml` | YAML parse |
| Transform exists | `.aiwg/mental_models/context_laplace_transform.md` | Manual review |
| State space parseable | `.aiwg/mental_models/context_state_space.json` | JSON parse |
| Per-message contract | `.aiwg/context_transform/per_message_operating_contract.yaml` | YAML parse |
| Receipt schema | `.aiwg/context_transform/context_transform_receipt.schema.json` | JSON parse |

## Acceptance

The mental model abstraction layer is accepted when the registry and state space parse, and the transform maps input signals to governed state.
