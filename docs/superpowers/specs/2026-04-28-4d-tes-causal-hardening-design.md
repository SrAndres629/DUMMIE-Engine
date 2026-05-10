# 4D-TES Causal Hardening Design

## Purpose

Turn the current 4D-TES/SDD implementation from a mix of promising modules and partial integrations into a stable, regression-resistant execution path. The immediate goal is not to invent a new theory surface, but to make the existing causal, epistemic, and governance primitives trustworthy under real test and audit conditions.

## Current State

The repository already contains:

- 4D-TES persistence and causal hashing in `layers/l2_brain/models.py`, `layers/l2_brain/adapters.py`, and `layers/l2_brain/orchestrator.py`.
- Experimental but valuable modules for entropy, counterfactual scoring, epistemic retrieval, runtime guards, causal replay, witness validation, and SDD governance.
- Real tests in `layers/l2_brain/tests`, but with path/import fragility and uneven coupling to production code.
- An industrial audit script and L1 crystallization path that currently fail under real execution.

The main gap is integration quality: multiple capabilities exist, but several are not yet mandatory execution gates, not yet wired through canonical contracts, or not yet robust across environments.

## Problem Statement

Three failure classes must be closed together:

1. Import and packaging fragility across L1/L2 and test environments.
2. Broken or stale compatibility surfaces in the 4D-TES persistence/audit path.
3. Governance primitives that exist as helpers but do not yet enforce execution decisions in the daemon or retrieval path.

## Design Principles

- Prefer compatibility-preserving contracts over test-only rewrites.
- Keep `MemoryNode4D` as the canonical schema contract and extend it through backward-compatible bridges.
- Promote causal/epistemic/governance primitives into execution gates only where a deterministic contract can be enforced.
- Add regression tests for every repaired failure mode before or alongside implementation.
- Keep scope focused on hardening existing architecture, not introducing new speculative data structures.

## Approaches Considered

### Option A: Minimal bugfixes only

Patch imports, fix the failing audit, and stop there.

Pros:
- Fastest path to green tests.

Cons:
- Leaves the daemon and retrieval path mostly aspirational.
- Preserves the exact gap that triggered the audit request.

### Option B: Full theoretical rewrite

Redesign the graph, schema, retrieval, and planner around new abstractions first.

Pros:
- Ambitious.

Cons:
- High regression risk.
- Violates the repo’s evolvability mandate by mixing concept work with stabilization.

### Option C: Progressive productionization of existing primitives

Stabilize contracts first, fix the real audit path, then wire existing governance/math modules into execution gates and retrieval flow with tests.

Pros:
- Directly addresses observed failures.
- Preserves current architecture while increasing real enforcement.
- Produces measurable improvement with contained diffs.

Cons:
- Less glamorous than a full redesign.

## Recommendation

Choose Option C.

The repo already contains the right raw materials. The highest-value work is to remove fragility, make compatibility explicit, and connect existing primitives to production paths so that the math and governance modules influence actual behavior rather than only tests or logs.

## Target Architecture

```text
L1 crystallization / audit / tools
  -> canonical L2 compatibility bridge
  -> MemoryNode4D canonical schema + compatibility helpers
  -> KuzuRepository stable query/persistence contract
  -> daemon execution gates
       - hierarchical planning
       - runtime guards
       - hypothesis entropy collapse
       - counterfactual admissibility
  -> retrieval path
       - epistemic ranking
       - optional minimal proof subgraph extraction
  -> verification
       - regression tests
       - industrial audit
       - docs/spec validation
```

## Components

### Contract Stability Layer

- Normalize L2 imports so modules work from both package-root and repo-root execution contexts.
- Reintroduce compatibility helpers expected by L1 tests and scripts where they represent legacy contract expectations rather than accidental test debt.

### Persistence and Audit Hardening

- Repair the L1 crystallization path so persistence succeeds and logs the actual causal hash.
- Ensure Kuzu schema creation and lookups work consistently regardless of execution context.
- Make the industrial audit script a trustworthy signal again.

### Execution Governance Hardening

- Convert runtime guard evaluation from optional tool logic into an explicit daemon gate.
- Use hypothesis entropy to decide whether a plan branch can collapse into execution.
- Use counterfactual scoring as an admissibility threshold instead of a log-only side effect.

### Retrieval Hardening

- Keep epistemic ranking in the repository path.
- Add a production entry point for minimal proof subgraph extraction so retrieval can return more than isolated ranked nodes when requested.
- Preserve backward compatibility for legacy plain-text payloads.

## Error Handling

- Persistence failures that matter to crystallization remain explicit failures.
- Guard failures return structured blocking/review outcomes rather than silent bypass.
- Compatibility helpers must not silently change canonical semantics; they only bridge legacy callers to the canonical contract.

## Testing Strategy

- Red-green tests for each repaired failure:
  - L1/L2 import stability.
  - `MemoryNode4D` compatibility helpers.
  - Kuzu repository schema bootstrap.
  - Crystallization persistence and industrial audit.
  - Daemon guard/collapse/admissibility behavior.
  - Retrieval minimal proof path.
- End with fresh execution of the relevant test suites, doc/spec validator, 4D-TES grep check, industrial audit, and repo diff inspection.

## Non-Goals

- No hypergraph/tensor/category rewrite in this pass.
- No schema-breaking change to `MemoryNode4D`.
- No global write interception beyond the daemon/runtime surfaces already present.
