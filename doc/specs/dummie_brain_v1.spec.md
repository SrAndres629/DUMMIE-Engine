# DUMMIE Brain MCP Specification v1.0

## Status: ACTIVE
**Contract Owner**: Antigravity
**Architecture**: Flat-L1 Gateway

## 1. Overview
The `dummie-brain` is the primary interface between the LLM (L2) and the DUMMIE Engine Infrastructure (L1). It acts as a gateway for both local capabilities (Loci Graph, 4D-TES) and remote capabilities (Swarm MCP Servers).

## 2. Information Model (Schemas)

### AuthorityLevel (Enum)
- `HUMAN`: Direct user intervention.
- `OVERSEER`: L0 Orchestrator authority.
- `AGENT`: Autonomous agent authority.

### SixDimensionalContext (Object)
- `locus_x` (string): Logic/Strategic dimension.
- `locus_y` (string): Transport/Tactical dimension.
- `locus_z` (string): Physical/Execution dimension.
- `lamport_t` (int): Causal timestamp.
- `authority_a` (AuthorityLevel): Identity of the actor.
- `intent_i` (IntentType): Semantic goal.

## 3. Toolset Definitions

### Category: Core (Diagnostic & Lifecycle)

#### `calibrate_neural_links`
- **Description**: Verifies health of Loci Graph and Decision Ledger.
- **Output**: Markdown report of connectivity status.

#### `brain_ping`
- **Description**: Lightweight heartbeat.
- **Output**: Status message with current Lamport clock.

### Category: Cognitive (Memory & Learning)

#### `crystallize`
- **Description**: Persists validated knowledge into 4D-TES.
- **Input**:
  - `payload` (string): Knowledge to persist.
  - `context` (SixDimensionalContext): Structural metadata.
- **Behavior**: Requires `RW` access to Loci Graph. Returns transaction hash.

#### `log_lesson`
- **Description**: Records learning from errors or sub-optimal paths.
- **Input**:
  - `issue` (string): Description of the problem.
  - `correction` (string): Path to avoid/resolve it.

### Category: Swarm (Coordination)

#### `broadcast_intent`
- **Description**: Publishes agent plan to the swarm ledger.
- **Input**:
  - `agent_id` (string): Identity of the broadcaster.
  - `intent` (string): Description of planned action.
  - `target_file` (string, optional): Affected resource.

#### `list_all_capabilities`
- **Description**: Discovery of all tools available in the swarm (local + remote).
- **Output**: JSON-structured inventory.

## 4. Architectural Constraints
1. **Purity**: Tools MUST NOT write to `stdout` except via the MCP protocol.
2. **Determinism**: All persistent actions MUST include a `lamport_t` timestamp.
3. **Fencing**: Tools MUST respect `read_only` locks on the memory plane.
