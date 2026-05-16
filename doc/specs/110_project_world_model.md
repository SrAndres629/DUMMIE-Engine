---
spec_id: "DE-V2-L2-110"
title: "ProjectWorldModel"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
version: "1.0.0"
namespace: "dummie.engine.plan_v1"
---
# Spec 110 - ProjectWorldModel

## Purpose
Create a compact, canonical, truth-governed project world model that future agents can load for global orientation without raw-repo reconstruction.

## Scope
Defines the world model fields, truth basis, compact loading rules, anti-bias guards, and downstream consumption contracts for P8 and later phases.

## Why P7 Exists
P1-P6.1 produced governance, artifact, truth, and polyglot contracts. P7 compiles these into one high-value context source that reduces chat-memory drift and Python-only bias.

## Current State
Implemented as world model JSON/MD, schema, phase report, and spec contract artifacts. Runtime enforcement is deferred.

## Physical Evidence
- `.aiwg/world_model/project_world_model.json`
- `.aiwg/world_model/project_world_model.md`
- `.aiwg/schemas/project_world_model.schema.json`
- `.aiwg/reports/plan_v1_phase_7_project_world_model.md`
- `.aiwg/reports/plan_v1_phase_7_project_world_model.json`
- `doc/specs/110_project_world_model.md`
- `doc/specs/110_project_world_model.feature`
- `doc/specs/110_project_world_model.rules.json`

## Relationship to P1-P6.1
P7 consumes:
- plan state and phase graph (`P1/P2`)
- artifact lifecycle and counting semantics (`P3`)
- cognitive artifact protocol (`P4`)
- truth hierarchy (`P5`)
- corrected polyglot registry (`P6/P6.1`)

## World Model Fields
Required fields include `current_state`, `roadmap_state`, `architecture_state`, `polyglot_state`, `truth_hierarchy_state`, `artifact_governance_state`, `capability_state`, `memory_state`, `spec_test_state`, `risk_register`, and `context_loading_policy`.

## Compact Context Requirement
World model must stay compact and reference canonical files instead of embedding massive inventories.

## Truth Basis
Truth basis must prioritize canonical phase state, schemas, and corrected registry artifacts over chat memory and mirror artifacts.

## Polyglot Bias Prevention
Global tasks must load:
- `.aiwg/architecture/polyglot_architecture_registry.yaml`
- `.aiwg/architecture/layer_language_map.json`

Python-only global summaries are invalid.

## Context Loading Policy
Use world model for stable orientation, reload `current_position.json` and `next_phase_seed.json` dynamically, and avoid bulk loading raw `.aiwg/memory` or `.aiwg/vault`.

## Freshness Expectations
Regenerate world model when plan state, truth schema, artifact schema, or polyglot registry changes materially.

## Relationship to P8 SpecCoverageGate
P8 must consume world model to create measurable spec/layer/language/test coverage gates.

## Relationship to P13 ContextQuantRuntime
P13 should treat world model as compact global context and use truth/artifact signals as scoring inputs.

## Relationship to Future CLI/Dashboard
Future interfaces may consume the world model, but dashboard views remain non-canonical projections unless promoted by policy.

## Validation Expectations
World model JSON, schema JSON, rules JSON, and report JSON must parse. Known inherited legacy spec debt remains tracked and non-regression-scoped.

## Contract Invariants
- World model is canonical compact orientation for global tasks.
- Dynamic phase state must be reloaded from evolution files.
- Polyglot and truth hierarchy artifacts are required for global reasoning.
- Raw repo bulk loading is not default strategy.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/110_project_world_model.md
python3 - <<'PY'
import json
from pathlib import Path
for p in [
    '.aiwg/world_model/project_world_model.json',
    '.aiwg/schemas/project_world_model.schema.json',
    'doc/specs/110_project_world_model.rules.json'
]:
    json.loads(Path(p).read_text(encoding='utf-8'))
print('spec 110 JSON evidence parse PASS')
PY
```

## Traceability
- Phase: `P7` ProjectWorldModel
- Depends on: `P1` to `P6.1`
- Next phase: `P8` SpecCoverageGate
