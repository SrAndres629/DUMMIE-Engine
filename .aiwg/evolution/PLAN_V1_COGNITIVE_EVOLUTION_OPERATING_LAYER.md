# DUMMIE PLAN V1 - Cognitive Evolution Operating Layer

DUMMIE PLAN V1 is the canonical operating roadmap for turning DUMMIE Engine into a cognitive software system that can manage long missions, short tactical objectives, phase state, context pressure, restart recovery, evidence, and progressive autonomy without drifting from repo truth.

It exists because DUMMIE must not operate as `prompt -> action -> report`. It must transform user objectives into governed cognitive state, select the correct phase, execute within scope, produce evidence, validate restart and hot paths, score snowball gain, update memory or reports, and seed the next phase.

The problem it solves is roadmap drift across CLI and IDE sessions. Chat memory, isolated reports, and local intuition are insufficient as sources of truth. The roadmap must be local, parseable, engine-native, and usable after restart.

## Snowball Phase

A snowball phase is a phase that makes later phases easier, safer, or more measurable. It must improve future execution through clearer contracts, stronger validation, better context selection, reusable evidence, or reduced manual intervention.

Una fase que agrega archivos pero no mejora capacidad medible es neutral o regresiva.

## Improvement

Real improvement means a phase creates measurable capability gain, improves future phase execution, reduces risk, increases evidence quality, strengthens restart survival, or improves hot-path operability. File count alone is not improvement.

## Restart Verification

Verified restart means a fresh agent can load canonical state from `.aiwg/evolution/`, identify the current phase, identify the next phase, discover session contracts, and continue without depending on chat memory.

## Hot-Path Verification

Verified hot path means an agent can start from `current_position.json`, load `next_phase_seed.json`, identify P2 as next, refuse forbidden skips, explain required P2 outputs, and locate session contracts.

## Context Transform

Context transform is the operational conversion of temporal events into governed state. Chat, reports, phases, errors, specs, memory, tests, file changes, agent outputs, and mentor reviews become objectives, invariants, dependencies, phase state, lifecycle state, truth hierarchy, next action, recovery packet, session contract, and snowball gain.

## Lifecycle

Lifecycle means every cognitive artifact must have a known role, freshness status, truth rank, ownership, and phase relationship. Phase 1 records the rule; later phases implement richer lifecycle runtimes.

## Strategic Partner

DUMMIE is a strategic partner, not a passive assistant. It must obey safety and scope boundaries while still reasoning strategically, recording objections when evidence contradicts a plan, and registering deferred capabilities instead of silently discarding them.

## Governance Across 31 Phases

Phase 1 creates the canonical operating layer for the next 30 phases. It defines the roadmap, dependencies, objectives, session contracts, acceptance criteria, restart protocol, hot-path protocol, and snowball metrics. Phase 2 through Phase 31 refine and implement future runtime capability under this layer.

Phase 1:
Mental Model Abstraction Layer + Session Operating Contract

Phase 2-31:
30 fases evolutivas de desarrollo, gobernanza, observabilidad, optimización, swarm y autonomía.

## Shared CLI/IDE Model

Gemini CLI, Codex CLI, and Antigravity IDE must operate from the same canonical model:

- load `.aiwg/evolution/current_position.json`;
- load `.aiwg/evolution/next_phase_seed.json`;
- check forbidden skips;
- use engine-native capabilities before adding new architecture;
- produce evidence reports;
- avoid storing secrets or private chain-of-thought;
- avoid redefining the roadmap from chat memory.

## Roadmap Source of Truth

The roadmap must not be redefined from chat memory because chat is temporal, partial, and session-bound. The canonical roadmap lives in `.aiwg/evolution/`, with specs in `doc/specs/`, schemas in `.aiwg/schemas/`, and evidence in `.aiwg/reports/`.

