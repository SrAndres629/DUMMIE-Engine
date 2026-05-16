# DUMMIE Project World Model (P7)

## What DUMMIE Is

DUMMIE is a layered polyglot cognitive-engineering system governed by Plan V1 contracts, phase state artifacts, truth hierarchy policy, and architecture registry constraints.

## Current Plan State

- Current phase: `P7` ProjectWorldModel.
- Last completed: `P6`.
- Next required phase: `P8` SpecCoverageGate.
- Current block: `truth_and_lifecycle`.

## Layered Architecture L0-L6

- `L0`: overseer/orchestration, daemon boundary.
- `L1`: nervous/protocol/gateway/data plane.
- `L2`: brain/cognition/memory/reasoning.
- `L3`: shield/security.
- `L4`: edge/adapters/sensors.
- `L5`: muscle/execution.
- `L6`: skin/UI.

Confidence is high for L0-L2, medium for L3-L5, low for L6 first-party UI identity.

## Polyglot Facts

- Python first-party spans L1-L6.
- Go first-party exists in L0/L1.
- Elixir first-party exists in L0 (`lib` + `test`) and is separated from dependency/build evidence (`deps`, `_build`).
- Rust first-party exists in L3.
- TypeScript/JavaScript evidence for L6 is dependency-only under `node_modules` in targeted scan.
- Protobuf serves as inter-layer contract shape.

## Truth Hierarchy Summary

- Code + passing tests are strongest behavioral truth.
- Specs are canonical intent; schemas are canonical shape.
- Reports are evidence, not primary truth.
- Mirrors and chat are non-canonical by default.
- Unsafe artifacts are hard-zero and excluded.

## Artifact Governance Summary

- Lifecycle matrix exists.
- Cognitive artifact protocol exists with lifecycle/canonicality/freshness/token/invalidation fields.
- Freshness and demotion are policy-bound; runtime enforcement remains phase-gated.

## Native Capabilities

Present and path-backed: `PhaseLedger`, `ContextBudgetManager`, `SemanticRetrievalRuntime`, `MemoryGraphRuntime`, `MissionWorkbench`, `OutcomeEvaluator`, `TokenCostLedger`, `SessionStore`, `LearningEpisode`, `VaultCurator`, `CognitiveHooks`, `ModelRouter`.

## Memory Systems

World model, reports, vault, session store, learning episodes, memory refs, graph sync plans, and semantic retrieval all coexist. Raw memory/vault dumps should not be bulk-loaded into prompts.

## Known Debt

- `DEBT-SPEC-LEGACY-MCP-GUIDE`
- `DEBT-AIWG-COUNTING-SEMANTICS`

## Context Loading Rules

- Use world model + current phase files for default orientation.
- Load polyglot registry for global architecture tasks.
- Load truth hierarchy and artifact schema for conflict/governance decisions.
- Avoid raw repo bulk scans unless a task requires deep evidence.

## Anti-Bias Guards

- Python-only global summaries are invalid.
- Chat-memory drift is blocked by canonical phase/registry/world model loading.
- Raw repo bulk loading is not default strategy.

## What P8 Must Do

P8 must convert this world model into measurable spec coverage gates across specs/rules/features, layer/language mapping, and test linkages while keeping legacy debt tracked as inherited.
