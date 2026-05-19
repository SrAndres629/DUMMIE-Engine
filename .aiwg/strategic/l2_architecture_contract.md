# L2 Brain — Architecture Contract

**Date:** 2026-05-19
**Status:** APPROVED by Jorge Andres Aguirre Cordero (Sovereign Architect)
**Version:** 1.0
**ADR Reference:** ADR-2026-05-19-L2-ARCH-001

---

## Sovereign Responsibility

L2 Brain is the **cognitive organ** of DUMMIE Engine.

**Responsibility:** Thinking, remembering, reasoning, deciding, evolving.

**NOT responsible for:**
- Transport/nervous system (L1)
- Security/shield (L3)
- Edge execution/scanning (L4)
- Observability/visualization (L5)
- Human interface (L6)

---

## Architectural Decisions (Approved by Jorge)

### Decision 1: flat_brain/ Status

```yaml
decision: "flat_brain/ is TEMP_COMPAT / MIGRATION_STAGING"
status: "NOT final architecture"
rationale: >
  ~180+ files migrated without manifest, 58+ specs broken, audit decision was FAIL.
  This describes an unsafe migration, not a designed architecture.
policy: >
  flat_brain/ modules remain functional via compatibility shim.
  No new modules added to flat_brain/.
  Modules will be reorganized into canonical L2 organs during PACK R3+.
```

### Decision 2: src/brain/ Status

```yaml
decision: "src/brain/ is seed architecture / DRAFT / partial target"
status: "NOT to be blindly absorbed or eliminated"
rationale: >
  Represents hexagonal/bounded-context thinking (4 contexts: context, memory,
  fabrication, governance per ADR 0009). Incomplete but architecturally sound.
policy: >
  Audit src/brain/ modules → classify → promote useful → archive dead → update specs/tests/imports.
  Do NOT delete src/brain/ until migration is complete.
  Do NOT absorb src/brain/ into flat_brain/.
```

### Decision 3: Test Location

```yaml
decision: "Tests remain separate in layers/l2_brain/tests/"
status: "Confirmed"
rationale: >
  Tests inside flat_brain/ would consolidate a non-final structure.
policy: >
  Tests stay in layers/l2_brain/tests/.
  Future: organize by organ (tests/context/, tests/memory/, tests/model_mesh/).
  Never inside flat_brain/.
```

### Decision 4: Persistence

```yaml
decision: "KùzuDB = canonical graph / 4D-TES memory"
status: "Confirmed"
rationale: >
  Kùzu adapter in L2 is the bridge for functional memory (per ADR 0011).
  Redb not declared as canonical memory in any evidence.
policy: >
  KùzuDB is the canonical persistence layer for L2 memory.
  Redb = optional KV/cache/snapshot layer only if specifically justified later.
  Do NOT add Redb "just in case" — that would add another source of truth.
```

### Decision 5: Import Strategy

```yaml
decision: "Compatibility shim stays, imports gradually migrate"
status: "Confirmed"
rationale: >
  FlatBrainRedirector shim exists and works (62 imports redirected).
  Breaking all imports at once is risky.
policy: >
  Shim remains as safety net.
  New code uses canonical import paths.
  Old imports gradually migrated during PACK R3+.
  Shim removed only when all imports use canonical paths.
```

---

## Canonical L2 Structure (Target)

Based on ADR 0009 (4 bounded contexts) + current functional analysis:

```
layers/l2_brain/
├── __init__.py              # Compatibility shim (stays until migration complete)
├── pyproject.toml
├── pytest.ini
│
├── context/                 # Bounded Context: Context Management
│   ├── __init__.py
│   ├── models.py            # 6D context, capsule models
│   ├── budget_manager.py
│   ├── compressor.py
│   ├── enforcement_gate.py
│   ├── package.py
│   ├── quant_runtime.py
│   ├── value_scorer.py
│   └── circulation.py
│
├── memory/                  # Bounded Context: Memory System (4D-TES + Kùzu)
│   ├── __init__.py
│   ├── models.py            # MemoryNode4D, TimeEvent, LociNode
│   ├── schemas.py           # Domain schemas
│   ├── ports.py             # Memory ports
│   ├── spine_bridge.py
│   ├── spine_entrypoint.py
│   ├── graph_runtime.py
│   ├── refs.py
│   ├── kuzu_adapter.py      # Canonical Kùzu adapter
│   └── kuzu_guard.py
│
├── model_mesh/              # Bounded Context: Model Routing & Embedding
│   ├── __init__.py
│   ├── router.py            # Model routing
│   ├── executor.py          # Model execution
│   ├── discovery.py         # Model discovery
│   ├── embedding_adapter.py
│   ├── embedding_memory_router.py
│   ├── embedding_provider.py
│   ├── embedding_activation_verifier.py
│   ├── mesh/                # Embedding mesh (providers, registry, reranking)
│   │   ├── __init__.py
│   │   ├── registry.py
│   │   ├── providers.py
│   │   ├── reranker.py
│   │   ├── repo_indexer.py
│   │   └── hardening_matrix.py
│   └── semantic_cache.py
│
├── cognition/               # Bounded Context: Reasoning & Decision
│   ├── __init__.py
│   ├── orchestrator.py      # Main cognitive orchestrator
│   ├── reasoning_logic.py
│   ├── counterfactual.py
│   ├── hypothesis.py
│   ├── local_reasoning.py
│   ├── consensus.py
│   ├── debate_review.py
│   ├── dialectical.py
│   ├── pattern_miner/       # Pattern mining
│   │   ├── __init__.py
│   │   ├── v1.py
│   │   └── v2.py
│   └── epistemic/           # Epistemic reasoning
│       ├── __init__.py
│       ├── judge.py
│       └── state_runtime.py
│
├── metacognition/           # Cross-cutting: Self-awareness
│   ├── __init__.py
│   ├── pipeline.py
│   ├── contracts.py
│   ├── input_hooks.py
│   ├── output_hooks.py
│   ├── deliberation_hooks.py
│   ├── reasoning_hooks.py
│   ├── semantic_hooks.py
│   ├── quality_gate.py
│   ├── evolution_flywheel.py
│   └── loop_runtime.py
│
├── mission/                 # Mission Orchestration
│   ├── __init__.py
│   ├── planner.py
│   ├── orchestrator_dag.py
│   ├── autonomy_contract.py
│   ├── coherence_guard.py
│   ├── runtime_contract.py
│   ├── workbench.py
│   ├── outcome_evaluator.py
│   └── long_running.py
│
├── strategic/               # Strategic Partner Runtime
│   ├── __init__.py
│   ├── partner_runtime.py
│   ├── partner_swarm.py
│   ├── business_advisor.py
│   ├── business_goal.py
│   ├── business_orchestrator.py
│   ├── goal_reasoning.py
│   └── revenue_planner.py
│
├── daemon/                  # Daemon & Runtime
│   ├── __init__.py
│   ├── daemon.py
│   ├── diagnostic.py
│   ├── gateway_heartbeat.py
│   └── outcome.py
│
├── heartbeat/               # Heartbeat System
│   ├── __init__.py
│   ├── decision_policy.py
│   ├── lifecycle_runtime.py
│   ├── scheduler.py
│   └── state_store.py
│
├── governance/              # Governance & Audit
│   ├── __init__.py
│   ├── kernel.py            # AIWG Kernel
│   ├── context_capsule.py
│   ├── auditor_port.py
│   ├── full_body_auditor.py
│   ├── whole_body_scanner.py
│   ├── whole_body_scan_calibrator.py
│   ├── whole_body_repair.py
│   ├── self_healing.py
│   ├── self_improvement.py
│   ├── post_mortem.py
│   └── supervisor_protocol.py
│
├── infrastructure/          # Infrastructure Layer (adapters, ports)
│   ├── __init__.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── kuzu.py
│   │   ├── ledger.py
│   │   ├── external.py
│   │   └── nats.py
│   ├── cognitive/
│   │   └── adapters.py
│   ├── reasoning/
│   │   └── providers.py
│   └── semantic_adapters.py
│
├── domain/                  # Shared Domain Models
│   ├── __init__.py
│   ├── dtos.py
│   ├── embedding_contract.py
│   ├── semantic_ports.py
│   ├── knowledge_ports.py
│   └── ports.py             # Canonical ports
│
├── sdk/                     # Client SDK
│   ├── __init__.py
│   ├── client.py
│   └── session.py
│
├── proto/                   # gRPC Definitions
│   └── proto/dummie/v2/
│
├── structural_hardening/    # Structural Hardening Tools
│   ├── __init__.py
│   ├── bindings.py
│   ├── classifier.py
│   ├── cli.py
│   ├── contracts.py
│   ├── evidence.py
│   └── matrix.py
│
├── tests/                   # Tests (SEPARATE, not inside any organ)
│   ├── test_*.py
│   └── infrastructure/
│
└── flat_brain/              # TEMP_COMPAT / MIGRATION_STAGING
    └── (all current flat_brain modules — to be migrated out)
```

---

## Migration Strategy

### Phase 1: Audit & Classify (PACK R3)

1. Audit every src/brain/ module → classify as PROMOTE / ARCHIVE / MERGE
2. Audit every flat_brain/ module → map to canonical organ
3. Create migration manifest with source → target mapping
4. Update specs to reference canonical paths

### Phase 2: Create Canonical Structure (PACK R4)

1. Create organ directories (context/, memory/, model_mesh/, etc.)
2. Move promoted src/brain/ modules to canonical locations
3. Move classified flat_brain/ modules to canonical locations
4. Update all imports to canonical paths
5. Update all tests to canonical paths

### Phase 3: Deprecate flat_brain/ (PACK R5)

1. Verify all imports use canonical paths
2. Verify all tests pass
3. Verify all specs reference canonical paths
4. Add deprecation warnings to flat_brain/ imports
5. Remove flat_brain/ directory
6. Remove compatibility shim from __init__.py

---

## Layer Boundaries

| Layer | Language | Responsibility | Interface to L2 |
|-------|----------|----------------|-----------------|
| L0 Overseer | Elixir | Supervision, fault tolerance | Protobuf over NATS |
| L1 Nervous | Go | Transport, causal hashing, NATS | gRPC + NATS events |
| **L2 Brain** | **Python** | **Cognition, memory, reasoning, strategy** | **gRPC client, NATS subscriber** |
| L3 Shield | Rust (planned) | Security, zero-trust, guardrails | Shield audit port |
| L4 Edge | Zig (planned) | Edge scanning, LST indexing | Scan commands |

---

## Invariants

1. **No module in flat_brain/ is SSoT.** All SSoT must be in canonical organs.
2. **No new modules added to flat_brain/.** New code goes to canonical organs.
3. **Tests never inside flat_brain/.** Tests stay in layers/l2_brain/tests/.
4. **KùzuDB is the only canonical persistence.** No Redb without justification.
5. **Compatibility shim is temporary.** Must be removed by PACK R5.
6. **All specs must reference canonical paths.** No spec references to flat_brain/.
