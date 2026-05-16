# DUMMIE PLAN V1 - P7 ProjectWorldModel

## Decision

PASS_WITH_WARNINGS

## Summary

P7 creates the first canonical ProjectWorldModel for compact global orientation, grounded in corrected polyglot evidence and truth-governed artifact policy.

## Advanced Reasoning Summary

Claims:
- Minimal canonical context is possible without raw-repo reconstruction.
- Global reasoning requires phase state + truth hierarchy + polyglot registry.
- A compact model can reduce token cost and drift while preserving governance fidelity.

Objections:
- Reports alone are stale-prone and cannot be primary truth.
- Static summaries drift if phase/registry state changes.
- Python-heavy file volume can bias global summaries unless guarded.

Decisions:
- Use world model JSON/MD as canonical global orientation layer.
- Keep phase state dynamic via current/next phase files.
- Require polyglot and truth artifacts for global tasks.
- Block raw vault/memory bulk loading by default.

Risks:
- Freshness drift without regeneration.
- Coverage uncertainty until P8.
- L6 first-party UI confidence remains low.

## World Model Created

- `.aiwg/world_model/project_world_model.json`
- `.aiwg/world_model/project_world_model.md`

## Schema Created

- `.aiwg/schemas/project_world_model.schema.json`

## Spec 110 Created

- `doc/specs/110_project_world_model.md`
- `doc/specs/110_project_world_model.feature`
- `doc/specs/110_project_world_model.rules.json`

## Canonical Inputs Consumed

- Evolution state and phase graph files.
- Cognitive artifact, truth hierarchy, and polyglot schemas.
- Corrected polyglot registry and layer map.
- P2-P6.1 phase reports as evidence inputs.

## Compact Context Policy

World model is the stable high-value orientation source. Future agents should load it plus dynamic phase files before global tasks, instead of defaulting to raw repo scans.

## Anti-Python-Only Bias Guard

Global tasks must load polyglot registry + layer map and report cross-layer coverage; Python-only global summaries are invalid.

## Chat Memory Drift Guard

Roadmap and state decisions must come from canonical evolution files, not chat memory.

## Raw Repo Bulk Load Guard

Raw `.aiwg/memory` and `.aiwg/vault` must not be bulk-loaded by default; use summary/reference strategy.

## Known Debt

- `DEBT-SPEC-LEGACY-MCP-GUIDE`
- `DEBT-AIWG-COUNTING-SEMANTICS`

## What P8 Must Consume

- `.aiwg/world_model/project_world_model.json`
- `.aiwg/architecture/polyglot_architecture_registry.yaml`
- `.aiwg/architecture/layer_language_map.json`
- `.aiwg/schemas/truth_hierarchy.schema.json`
- `.aiwg/schemas/cognitive_artifact.schema.json`

## Remaining Risks

- World model freshness drift if canonical inputs change.
- Spec/test/layer coverage confidence is still uneven before coverage gating.

## Next Phase

P8 - SpecCoverageGate
