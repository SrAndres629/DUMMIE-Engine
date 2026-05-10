# Sovereign SDD Governance Design

## Purpose

Turn the 4D-TES from persistent memory into a causal control system for Spec-Driven Development. Specs become executable intent sources. Code changes must prove lineage, authority, evidence, and architectural fitness before promotion.

## Integrated Improvements

This design integrates the proposed improvements from the human architect and the assistant:

- Causal Replay for time-travel debugging of agent decisions.
- Necro-Learning and semantic entropy promotion/demotion.
- Nervous Pulse for stale-spec interruption across agents.
- Semantic Graph RAG for intent-level explanation retrieval.
- Witness Protocol for deterministic causal-chain validation.
- Recursive self-optimization based on repeated failure loci.
- Formal Verification Bridge as an optional authority source.
- Spec Compiler.
- Change Admission Control.
- Evidence Graph.
- Architecture Fitness Functions.
- Spec Coverage.
- Contradiction Engine.
- Decision Decay.
- Golden Path generation.
- Runtime Causal Guards.
- Human Intent Calibration.
- Branch/Workroom Memory.
- Failure Taxonomy.

## Core Thesis

The spec is the genotype. Code, tests, docs, and runtime behavior are phenotypes. A change without a causal parent spec is not merely undocumented; it is architecturally inadmissible.

## Architecture

```text
Spec Markdown
  -> Spec Compiler
  -> SpecNode
  -> Change Admission Control
  -> Evidence Graph
  -> Architecture Fitness Functions
  -> 4D-TES Crystallization
  -> Causal Replay / Semantic RAG / Nervous Pulse
```

## Governance Loop

1. Compile specs into `SpecNode` records.
2. Validate requested changes against approved specs.
3. Attach evidence and tests to every claim.
4. Run architecture fitness functions.
5. Admit, review, or block the change.
6. Record decisions and failures in the 4D-TES.
7. Use replay, entropy, and pulses to keep agents coherent over time.

## Initial Implementation Boundary

The first physical implementation is pure L2 logic:

- `sdd_governance.py` for spec compilation, admission control, evidence graph, contradictions, decision decay, coverage, and failure taxonomy.
- `causal_replay.py` for reconstructing replay frames from events.
- `runtime_guards.py` for provider/spec readiness guards.

No write interception is installed at L1 yet. This avoids blocking current workflows before the governance rules are proven.

## Non-Goals

- Do not implement TLA+/Coq execution in this phase.
- Do not block filesystem writes globally in this phase.
- Do not mutate 4D-TES schema in this phase.
- Do not replace existing specs.
