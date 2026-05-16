# DUMMIE Systemic Refactor Roadmap

## Status Summary

DUMMIE has transitioned from "ideas" to a "wired" state with the implementation of the `CognitiveHookPipeline` and `SensorFirstPolicy`. However, the system is not yet "operational" as a self-improving organism. The critical gap is the lack of a closed-loop system that measures performance, stores structured artifacts per mission, and distills experience into a permanent vault.

## Component Assessment

| Component | Current State | Missing Connection | What it Unlocks | Recommended Phase |
| :--- | :--- | :--- | :--- | :--- |
| **CognitiveHookPipeline** | Operational | Feedback loop from evaluation | Dynamic authority adjustment | 0 |
| **SensorFirstPolicy** | Operational | Enforcement in all read paths | Drastic token reduction | 1 |
| **MetaGatewayRuntimeMeter** | Operational | Integration into Daemon flow | Empirical efficiency proof | 1 |
| **TokenCostLedger** | Operational | LearningEpisode data stream | Real-time economy management | 2 |
| **MissionWorkbench** | Operational | Filesystem artifact storage | Transparency and persistence | 3 |
| **VaultCurator** | Operational | Workbench -> Vault pipeline | Long-term learning crystallization | 3 |
| **LearningEpisode** | Operational | SessionStore / 4D-TES | Causal memory association | 4 |
| **MissionOrchestrator** | Wired (Basic) | DAG / MissionState persistence | Multi-step complex missions | 5 |
| **LocalModelRuntime** | Declared | PromptRefiner / Summarizer | Low-cost pre-processing | 6 |
| **StrategicPartnerSwarm** | Declared | Agent Contracts | Specialized role collaboration | 7 |

## Refactor Order

### Phase 1: Stabilization & Hardening (Next Slice)
*   **Goal:** Eliminate authority false positives and enforce Sensor-First.
*   **Deliverables:**
    *   Authority regression test suite.
    *   `MetaGatewayRuntimeMeter` integration in `DummieDaemon`.
    *   Hardened `SensorFirstPolicy` with `BLOCK` mode for high-risk discovery.

### Phase 2: Runtime Economy
*   **Goal:** Measure every token and byte.
*   **Deliverables:**
    *   `TokenCostLedger` implementation.
    *   `ContextBudgetManager` integration.

### Phase 3: Mission Persistence (The Workbench)
*   **Goal:** Create a physical workspace for every task.
*   **Deliverables:**
    *   `MissionWorkbench` structure in `.aiwg/workbench/`.
    *   `VaultCurator` to extract "Golden Paths".

### Phase 4: Cognitive Memory
*   **Goal:** Connect experience to the 4D-TES.
*   **Deliverables:**
    *   `LearningEpisode` persistence in `SessionStore`.
    *   Pattern discovery from failed sagas.

### Phase 5: Advanced Orchestration
*   **Goal:** Move from linear sagas to Mission DAGs.
*   **Deliverables:**
    *   `MissionOrchestrator` DAG support.
    *   Agent Swarm with role-based contracts.

## Next Patch: Phase 1 - Stabilization & Metering

The immediate next step is to harden the `SensorFirstPolicy` and start measuring efficiency in real-time. This provides the empirical baseline needed to justify more complex organs like the Workbench and Vault.
