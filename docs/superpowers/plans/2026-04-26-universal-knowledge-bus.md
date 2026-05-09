# Universal Knowledge Bus Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the provider-agnostic knowledge bus that lets Obsidian hydrate, mirror, and rehydrate the 4D-TES without making L2 provider-aware.

**Architecture:** Implement the core contracts in L2 first, harden MCP readiness in L1, add L3 write policy, then add Obsidian as the first external adapter. Advanced features are phased: entropy signals, pre-flight drafts, swarm consensus mirrors, and conservative rehydration.

**Tech Stack:** Python 3.11+, existing FastMCP gateway, JSON Schema-compatible dict contracts, pytest, current L1/L2/L3 layer structure.

---

## Chunk 1: Core Bus Contracts

### Task 1: Add Provider-Agnostic Models

**Files:**
- Modify: `layers/l2_brain/models.py`
- Test: `layers/l2_brain/tests/test_domain_models.py`

- [ ] **Step 1: Write failing tests for source artifacts**

Add tests that instantiate `SourceArtifact`, `MemoryTemperatureSignal`, `IntentDraft`, `ConsensusDecision`, and `RehydrationManifest`.

Expected assertions:

```python
def test_source_artifact_requires_provider_and_hash():
    artifact = SourceArtifact(
        provider="obsidian",
        source_uri="obsidian://Decisions/OBS-001.md",
        content_type="text/markdown",
        content="body",
        payload_hash="abc123abc123abc123",
        observed_at="2026-04-26T00:00:00Z",
        metadata={"path": "Decisions/OBS-001.md"},
    )
    assert artifact.provider == "obsidian"
    assert artifact.payload_hash.startswith("abc123")
```

- [ ] **Step 2: Run model tests and confirm failure**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests/test_domain_models.py
```

Expected: fails because the new classes do not exist.

- [ ] **Step 3: Implement dataclasses**

Add focused dataclasses and enums to `layers/l2_brain/models.py`:

```python
class MemoryTemperature(Enum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    QUARANTINED = "QUARANTINED"

@dataclass
class SourceArtifact:
    provider: str
    source_uri: str
    content_type: str
    content: str
    payload_hash: str
    observed_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)
```

Add equivalent dataclasses for the remaining contracts.

- [ ] **Step 4: Run model tests**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests/test_domain_models.py
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add layers/l2_brain/models.py layers/l2_brain/tests/test_domain_models.py
git commit -m "feat: add universal knowledge bus domain models"
```

### Task 2: Add L2 Knowledge Ports

**Files:**
- Create: `layers/l2_brain/knowledge_ports.py`
- Test: `layers/l2_brain/tests/test_knowledge_ports.py`

- [ ] **Step 1: Write failing protocol/import tests**

Create tests that import `KnowledgeProvider`, `WisdomPublisher`, `EntropyGovernor`, and `RehydrationProvider`.

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests/test_knowledge_ports.py
```

Expected: import failure.

- [ ] **Step 3: Implement ports using `typing.Protocol`**

Define provider-agnostic methods only:

```python
class KnowledgeProvider(Protocol):
    async def search_context(self, query: str, limit: int = 10) -> list[SourceArtifact]: ...
    async def get_artifact(self, source_uri: str) -> SourceArtifact: ...

class WisdomPublisher(Protocol):
    async def publish_decision(self, decision: ConsensusDecision) -> str: ...
    async def publish_lesson(self, issue: str, correction: str) -> str: ...
```

- [ ] **Step 4: Run tests**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests/test_knowledge_ports.py
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add layers/l2_brain/knowledge_ports.py layers/l2_brain/tests/test_knowledge_ports.py
git commit -m "feat: define provider-agnostic knowledge ports"
```

## Chunk 2: MCP Protocol Hardening

### Task 3: Add MCP Connection State

**Files:**
- Modify: `layers/l1_nervous/mcp_proxy.py`
- Test: `layers/l1_nervous/tests/test_mcp_proxy_handshake.py`

- [ ] **Step 1: Write failing state transition tests**

Test that a server starts in `INIT`, cannot call tools before `READY`, and reaches `READY` only after initialize, initialized notification, and tools/list.

- [ ] **Step 2: Run the focused test**

Run:

```bash
PYTHONPATH="layers/l2_brain:layers/l1_nervous" pytest -q layers/l1_nervous/tests/test_mcp_proxy_handshake.py
```

Expected: failure because state machine is missing.

- [ ] **Step 3: Implement state enum and readiness guard**

Add:

```python
class MCPConnectionState(str, Enum):
    INIT = "INIT"
    WAIT_SERVER = "WAIT_SERVER"
    HANDSHAKE_OK = "HANDSHAKE_OK"
    DISCOVERY = "DISCOVERY"
    READY = "READY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
```

Block `call_tool` unless the connection is ready, except internal handshake/discovery calls.

- [ ] **Step 4: Run the focused test**

Run the same command. Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add layers/l1_nervous/mcp_proxy.py layers/l1_nervous/tests/test_mcp_proxy_handshake.py
git commit -m "feat: enforce deterministic MCP readiness"
```

### Task 4: Add Fake MCP Server Integration Test

**Files:**
- Create: `layers/l1_nervous/tests/fixtures/fake_mcp_obsidian.py`
- Modify: `layers/l1_nervous/tests/test_mcp_proxy_handshake.py`

- [ ] **Step 1: Create a fake stdio MCP server fixture**

The fake server must implement:

- `initialize`
- `notifications/initialized`
- `tools/list`
- `tools/call`

- [ ] **Step 2: Test discovery cache**

Assert that discovered tools include only the expected Obsidian allowlist.

- [ ] **Step 3: Run integration test**

Run:

```bash
PYTHONPATH="layers/l2_brain:layers/l1_nervous" pytest -q layers/l1_nervous/tests/test_mcp_proxy_handshake.py
```

Expected: pass.

- [ ] **Step 4: Commit**

```bash
git add layers/l1_nervous/tests/fixtures/fake_mcp_obsidian.py layers/l1_nervous/tests/test_mcp_proxy_handshake.py
git commit -m "test: cover MCP discovery with fake obsidian server"
```

## Chunk 3: Obsidian Adapter And L3 Policy

### Task 5: Add L1 Obsidian Adapter

**Files:**
- Create: `layers/l1_nervous/knowledge_adapters.py`
- Test: `layers/l1_nervous/tests/test_obsidian_knowledge_adapter.py`

- [ ] **Step 1: Write failing adapter tests**

Use a fake proxy manager. Assert:

- `search_context` calls `obsidian_simple_search`
- `get_artifact` calls `obsidian_get_file_contents`
- returned data is converted to `SourceArtifact`

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
PYTHONPATH="layers/l2_brain:layers/l1_nervous" pytest -q layers/l1_nervous/tests/test_obsidian_knowledge_adapter.py
```

- [ ] **Step 3: Implement minimal adapter**

Keep provider-specific logic in L1. Do not import adapter from L2.

- [ ] **Step 4: Run adapter tests**

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add layers/l1_nervous/knowledge_adapters.py layers/l1_nervous/tests/test_obsidian_knowledge_adapter.py
git commit -m "feat: add obsidian knowledge adapter"
```

### Task 6: Add L3 Write Policy

**Files:**
- Create: `layers/l3_shield/knowledge_policy.py`
- Test: `layers/l3_shield/tests/test_knowledge_policy.py`

- [ ] **Step 1: Write policy matrix tests**

Assert:

- read/search/batch read are allowed
- append through sovereign wrapper is allowed
- patch/put/delete return `L3_INTERVENTION_REQUIRED`
- unknown write operations are denied

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
pytest -q layers/l3_shield/tests/test_knowledge_policy.py
```

- [ ] **Step 3: Implement policy**

Use simple pure functions first:

```python
def evaluate_knowledge_write(operation: str, wrapper: str | None = None) -> str:
    ...
```

- [ ] **Step 4: Run policy tests**

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add layers/l3_shield/knowledge_policy.py layers/l3_shield/tests/test_knowledge_policy.py
git commit -m "feat: add L3 knowledge write policy"
```

## Chunk 4: Sovereign Wrappers

### Task 7: Register Read Wrappers

**Files:**
- Create: `layers/l1_nervous/tools_impl/knowledge.py`
- Modify: `layers/l1_nervous/tools.py`
- Test: `layers/l1_nervous/tests/test_knowledge_tools.py`

- [ ] **Step 1: Write failing tests for wrapper registration**

Assert tools exist by name:

- `knowledge_search_context`
- `knowledge_get_artifact`
- `knowledge_ingest_artifact`

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
PYTHONPATH="layers/l2_brain:layers/l1_nervous" pytest -q layers/l1_nervous/tests/test_knowledge_tools.py
```

- [ ] **Step 3: Implement registration**

Register provider-agnostic names. Internally route to the configured provider adapter.

- [ ] **Step 4: Run tests**

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add layers/l1_nervous/tools.py layers/l1_nervous/tools_impl/knowledge.py layers/l1_nervous/tests/test_knowledge_tools.py
git commit -m "feat: expose provider-agnostic knowledge tools"
```

### Task 8: Register Journal/Wisdom Wrappers

**Files:**
- Modify: `layers/l1_nervous/tools_impl/knowledge.py`
- Test: `layers/l1_nervous/tests/test_knowledge_tools.py`

- [ ] **Step 1: Write tests for append-only wrappers**

Assert:

- `knowledge_export_decision_summary` uses append policy
- `knowledge_export_lesson` uses append policy
- `knowledge_export_session_summary` uses append policy
- patch/put/delete are unavailable from wrapper API

- [ ] **Step 2: Run tests and confirm failure**

Run the same test file.

- [ ] **Step 3: Implement wrappers**

Use L3 policy before calling any provider write operation.

- [ ] **Step 4: Run tests**

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add layers/l1_nervous/tools_impl/knowledge.py layers/l1_nervous/tests/test_knowledge_tools.py
git commit -m "feat: add append-only wisdom publisher tools"
```

## Chunk 5: Advanced Capabilities

### Task 9: Semantic Entropy Governor

**Files:**
- Create: `layers/l2_brain/entropy_governor.py`
- Test: `layers/l2_brain/tests/test_entropy_governor.py`

- [ ] **Step 1: Write tests for temperature classification**

Assert human edit/manual pin increases temperature and conflict/quarantine lowers operational availability.

- [ ] **Step 2: Implement pure scorer**

Do not delete memory. Return temperature recommendation and rationale.

- [ ] **Step 3: Run tests**

```bash
cd layers/l2_brain && uv run pytest -q tests/test_entropy_governor.py
```

- [ ] **Step 4: Commit**

```bash
git add layers/l2_brain/entropy_governor.py layers/l2_brain/tests/test_entropy_governor.py
git commit -m "feat: add semantic entropy governor"
```

### Task 10: Pre-Flight Drafts

**Files:**
- Create: `layers/l2_brain/preflight.py`
- Test: `layers/l2_brain/tests/test_preflight.py`

- [ ] **Step 1: Test draft generation from high-risk intent**

Assert `IntentDraft.requires_human_review` is true for high-risk operations.

- [ ] **Step 2: Implement draft builder**

Return an `IntentDraft`; do not write files directly from L2.

- [ ] **Step 3: Run tests**

```bash
cd layers/l2_brain && uv run pytest -q tests/test_preflight.py
```

- [ ] **Step 4: Commit**

```bash
git add layers/l2_brain/preflight.py layers/l2_brain/tests/test_preflight.py
git commit -m "feat: add pre-flight intent drafts"
```

### Task 11: Swarm Consensus Mirrors

**Files:**
- Create: `layers/l2_brain/consensus.py`
- Test: `layers/l2_brain/tests/test_consensus.py`

- [ ] **Step 1: Test consensus promotion**

Assert observations and evidence produce a `ConsensusDecision` with dissent preserved.

- [ ] **Step 2: Implement pure consensus builder**

No provider writes in L2.

- [ ] **Step 3: Run tests**

```bash
cd layers/l2_brain && uv run pytest -q tests/test_consensus.py
```

- [ ] **Step 4: Commit**

```bash
git add layers/l2_brain/consensus.py layers/l2_brain/tests/test_consensus.py
git commit -m "feat: add consensus decision builder"
```

### Task 12: Deep Memory Rehydration Dry Run

**Files:**
- Create: `layers/l2_brain/rehydration.py`
- Test: `layers/l2_brain/tests/test_rehydration.py`

- [ ] **Step 1: Test dry-run manifest parsing**

Assert a `RehydrationManifest` produces candidate decisions and lessons but does not mutate the event store.

- [ ] **Step 2: Implement dry-run parser**

Keep implementation conservative: parse provenance blocks and headings from supplied artifacts.

- [ ] **Step 3: Run tests**

```bash
cd layers/l2_brain && uv run pytest -q tests/test_rehydration.py
```

- [ ] **Step 4: Commit**

```bash
git add layers/l2_brain/rehydration.py layers/l2_brain/tests/test_rehydration.py
git commit -m "feat: add conservative rehydration dry run"
```

## Chunk 6: Configuration And Verification

### Task 13: Add Disabled Obsidian Registry Entry

**Files:**
- Modify: `dummie_agent_config.json`
- Create: `docs/ops/obsidian-knowledge-bus.md`

- [ ] **Step 1: Add disabled config**

Add server entry with `"disabled": true` and placeholder env names. Do not commit secrets.

- [ ] **Step 2: Document setup**

Explain Obsidian Local REST API requirement and the default disabled posture.

- [ ] **Step 3: Validate JSON**

Run:

```bash
python3 -m json.tool dummie_agent_config.json >/tmp/dummie_agent_config.validated.json
```

- [ ] **Step 4: Commit**

```bash
git add dummie_agent_config.json docs/ops/obsidian-knowledge-bus.md
git commit -m "docs: add disabled obsidian knowledge bus config"
```

### Task 14: Full Regression Verification

**Files:**
- No source edits unless failures reveal issues.

- [ ] **Step 1: Run L2 tests**

```bash
cd layers/l2_brain && uv run pytest -q tests
```

- [ ] **Step 2: Run L1 focused tests**

```bash
PYTHONPATH="layers/l2_brain:layers/l1_nervous" pytest -q layers/l1_nervous/tests
```

- [ ] **Step 3: Run L3 policy tests**

```bash
pytest -q layers/l3_shield/tests/test_knowledge_policy.py
```

- [ ] **Step 4: Run import smoke**

```bash
PYTHONPATH="layers/l2_brain:layers/l1_nervous:layers/l3_shield:layers/l4_edge:layers/l5_muscle" layers/l2_brain/.venv/bin/python -c "import models, orchestrator, bootstrap, tools, resources"
```

- [ ] **Step 5: Record evidence**

Save command outputs in the final implementation summary. Do not claim completion without fresh passing output.
