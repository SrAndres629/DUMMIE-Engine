# DUMMIE PLAN V1 - P6 PolyglotArchitectureRegistry

## Decision

PASS_WITH_WARNINGS

## Summary

P6 creates the canonical polyglot architecture registry from tracked physical repo evidence. It separates first-party architecture from dependency/generated/configuration/documentation counts and blocks Python-only global summaries.

## Advanced Reasoning Summary

Claims:
- DUMMIE cannot be globally understood from L2/Python only.
- Language/layer mapping must be canonical before ProjectWorldModel.
- Vendored/dependency code must not define architectural identity.

Objections:
- File counts can be misleading because deps/build/node_modules are tracked.
- Some layers have sparse or ambiguous implementation relative to specs.
- Specs may describe more than current physical code proves.

Decisions:
- Registry uses `git ls-files` and physical paths as evidence.
- Registry distinguishes first_party from dependency/generated/config/docs.
- Future global tasks must load registry and report language coverage.
- P7 must consume registry instead of inferring architecture from memory.

Risks:
- Registry is only as fresh as commit `cf56165d42e735297994d049ff66e4b494283e48`.
- Layer naming may drift.
- Some language roles need refinement after P7/P8.

## Physical Scan Method

Used `git ls-files` for tracked file evidence and `find layers -maxdepth 3 -type d` for layer directories. Large inventories are summarized in registry samples.

## Languages Found

Python, Go, Elixir, Rust, TypeScript, JavaScript, Protobuf, Shell, YAML/JSON/TOML, Markdown/spec docs.

## First-Party vs Dependency/Vendored Distinction

First-party source is separated from dependency/generated/configuration/documentation classifications. Tracked `deps`, `_build`, `node_modules`, `.venv`, `target`, and `generated` paths are treated as non-identity evidence for architecture.

## Layer-Language Map

All L0-L6 layers are present in `.aiwg/architecture/layer_language_map.json`; low or medium confidence indicates sparse/ambiguous first-party evidence, not absence from the roadmap.

## Runtime Roles

Runtime roles are summarized by layer: L0 overseer/orchestration, L1 nervous/protocols, L2 brain/cognition, L3 shield/security, L4 edge/adapters, L5 muscle/execution, L6 skin/UI.

## Specs and Tests Coverage

Specs are sampled per layer from `doc/specs/L*_...`; tests are sampled from layer-local `test`/`tests` paths where present. P8 must refine coverage gates.

## Anti-Python-Only Bias Guard

Future global architecture tasks must load `.aiwg/architecture/polyglot_architecture_registry.yaml` and `.aiwg/architecture/layer_language_map.json` before producing global summaries.

## Registry Created

- `.aiwg/architecture/polyglot_architecture_registry.yaml`
- `.aiwg/architecture/layer_language_map.json`

## Schema Created

- `.aiwg/schemas/polyglot_architecture_registry.schema.json`

## Spec 109 Created

- `doc/specs/109_polyglot_architecture_registry.md`
- `doc/specs/109_polyglot_architecture_registry.feature`
- `doc/specs/109_polyglot_architecture_registry.rules.json`

## What P7 Must Consume

- `.aiwg/architecture/polyglot_architecture_registry.yaml`
- `.aiwg/architecture/layer_language_map.json`
- `.aiwg/schemas/polyglot_architecture_registry.schema.json`
- `doc/specs/109_polyglot_architecture_registry.md`

## Known Debt

- `DEBT-SPEC-LEGACY-MCP-GUIDE`

## Remaining Risks

- Raw language counts remain noisy because dependency/generated folders are tracked.
- P7/P8 should refine owner/runtime confidence and coverage gates.

## Next Phase

P7 - ProjectWorldModel
