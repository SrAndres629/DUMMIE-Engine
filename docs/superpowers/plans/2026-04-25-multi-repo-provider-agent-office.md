# Multi-Repo Provider Agent Office Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the MVP runtime for a multi-repo, multi-provider agent office with repo-local 4D memory, WorkRooms, scoped context packets, evidence packets, and auditable session lifecycle.

**Architecture:** Implement stable contracts first using small Python modules under L2, backed by repo-local JSON/JSONL storage in `.aiwg`. Start with a path-based SpecGraph and a local/manual provider adapter, then add real provider adapters once the contracts are proven.

**Tech Stack:** Python dataclasses or Pydantic-style models if already available, pytest, repo-local `.aiwg`, JSON/JSONL, existing DUMMIE L2/L4 layout.

---

## Implementation Strategy

This plan intentionally avoids building a large autonomous swarm first. The first milestone is a durable, testable control loop:

```text
RepoManifest -> WorkRoom -> ContextPacket -> AgentSession -> EvidencePacket -> DecisionRecord -> Close WorkRoom
```

Provider integrations come after this loop is stable.

## File Structure

Create a focused runtime package:

```text
layers/l2_brain/agent_office/
  __init__.py
  models.py
  repo_runtime.py
  specgraph.py
  context_builder.py
  providers.py
  orchestrator.py
  storage.py
```

Tests:

```text
layers/l2_brain/tests/test_agent_office_models.py
layers/l2_brain/tests/test_agent_office_storage.py
layers/l2_brain/tests/test_agent_office_specgraph.py
layers/l2_brain/tests/test_agent_office_context_builder.py
layers/l2_brain/tests/test_agent_office_orchestrator_flow.py
```

Responsibilities:

- `models.py`: pure data contracts.
- `storage.py`: repo-local JSON/JSONL persistence.
- `repo_runtime.py`: loads repo manifest and resolves `.aiwg`.
- `specgraph.py`: maps files to specs/rules/features using deterministic path rules.
- `context_builder.py`: creates scoped ContextPackets.
- `providers.py`: defines provider adapter interface and manual/local adapter.
- `orchestrator.py`: opens/closes WorkRooms and records evidence/decisions.

## Chunk 1: Core Contracts

### Task 1: Define Agent Office Models

**Files:**
- Create: `layers/l2_brain/agent_office/__init__.py`
- Create: `layers/l2_brain/agent_office/models.py`
- Create: `layers/l2_brain/tests/test_agent_office_models.py`

- [ ] **Step 1: Write model tests**

Test required fields and JSON-safe conversion for:

- `RepoManifest`
- `WorkRoom`
- `AgentSession`
- `ContextPacket`
- `EvidencePacket`
- `DecisionRecord`

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests/test_agent_office_models.py
```

Expected before implementation:

```text
ModuleNotFoundError or ImportError
```

- [ ] **Step 2: Implement minimal models**

Use dataclasses and `asdict` to avoid adding dependencies unless the repo already standardizes on another model library.

Required enums or literal status values:

- WorkRoom: `OPEN`, `REVIEW`, `APPROVED`, `REJECTED`, `CLOSED`
- AgentSession: `OPEN`, `CLOSED`, `FAILED`
- EvidencePacket: `PENDING`, `VERIFIED`, `REJECTED`
- DecisionRecord: `PROPOSED`, `APPROVED`, `REJECTED`

- [ ] **Step 3: Run tests**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests/test_agent_office_models.py
```

Expected:

```text
passed
```

## Chunk 2: Repo-Local Storage

### Task 2: Implement `.aiwg` Runtime Storage

**Files:**
- Create: `layers/l2_brain/agent_office/storage.py`
- Create: `layers/l2_brain/agent_office/repo_runtime.py`
- Create: `layers/l2_brain/tests/test_agent_office_storage.py`

- [ ] **Step 1: Write storage tests**

Use `tmp_path` to create a fake repo root. Verify:

- `repo.json` is created.
- WorkRoom JSON writes under `.aiwg/workrooms/`.
- ContextPacket JSON writes under `.aiwg/context-packets/`.
- EvidencePacket JSON writes under `.aiwg/evidence/`.
- No writes escape the repo root.

- [ ] **Step 2: Implement storage**

Keep storage boring:

- atomic-ish write via temp file then replace,
- UTF-8 JSON with sorted keys,
- no global state,
- repo root passed explicitly.

- [ ] **Step 3: Run tests**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests/test_agent_office_storage.py
```

Expected:

```text
passed
```

## Chunk 3: Path-Based SpecGraph

### Task 3: Map Files to Specs

**Files:**
- Create: `layers/l2_brain/agent_office/specgraph.py`
- Create: `layers/l2_brain/tests/test_agent_office_specgraph.py`

- [ ] **Step 1: Write specgraph tests**

Use fake repo files:

```text
layers/l2_brain/daemon.py
layers/l5_muscle/mcp_driver.py
doc/specs/02_memory_engine_4d_tes.md
doc/specs/02_memory_engine_4d_tes.rules.json
doc/specs/02_memory_engine_4d_tes.feature
doc/specs/05_orchestration_stack_and_glue.md
```

Assert:

- L2 files map to L2 specs.
- L5 files map to L5 specs.
- `.rules.json` and `.feature` siblings are linked when present.
- Missing specs return empty lists, not crashes.

- [ ] **Step 2: Implement deterministic path rules**

Start with simple layer mapping:

```text
layers/l0_overseer/** -> L0
layers/l1_nervous/** -> L1
layers/l2_brain/** -> L2
layers/l3_shield/** -> L3
layers/l4_edge/** -> L4
layers/l5_muscle/** -> L5
layers/l6_skin/** -> L6
```

- [ ] **Step 3: Run tests**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests/test_agent_office_specgraph.py
```

Expected:

```text
passed
```

## Chunk 4: Context Packet Builder

### Task 4: Build Role-Scoped Context

**Files:**
- Create: `layers/l2_brain/agent_office/context_builder.py`
- Create: `layers/l2_brain/tests/test_agent_office_context_builder.py`

- [ ] **Step 1: Write context builder tests**

Verify:

- Researcher gets read-only constraints.
- Implementer gets ownership constraints.
- Verifier gets command/evidence obligations.
- Context includes only requested files and mapped specs.
- Context includes output schema name.

- [ ] **Step 2: Implement builder**

Input:

- repo manifest,
- workroom,
- role,
- task,
- file paths,
- specgraph result.

Output:

- `ContextPacket`.

- [ ] **Step 3: Run tests**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests/test_agent_office_context_builder.py
```

Expected:

```text
passed
```

## Chunk 5: Provider Adapter Contract

### Task 5: Define Provider Interface and Manual Adapter

**Files:**
- Create: `layers/l2_brain/agent_office/providers.py`
- Create: `layers/l2_brain/tests/test_agent_office_provider_adapter.py`

- [ ] **Step 1: Write provider tests**

Verify:

- adapter receives a ContextPacket,
- adapter returns an AgentSession and placeholder output,
- manual adapter does not call network,
- provider metadata records provider/model/role.

- [ ] **Step 2: Implement provider interface**

Define:

```python
class ProviderAdapter(Protocol):
    async def open_session(self, context_packet: ContextPacket) -> AgentSession: ...
    async def close_session(self, session_id: str) -> None: ...
```

Manual adapter can return a deterministic `AgentSession` for MVP.

- [ ] **Step 3: Run tests**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests/test_agent_office_provider_adapter.py
```

Expected:

```text
passed
```

## Chunk 6: Orchestrator Flow

### Task 6: Implement MVP WorkRoom Lifecycle

**Files:**
- Create: `layers/l2_brain/agent_office/orchestrator.py`
- Create: `layers/l2_brain/tests/test_agent_office_orchestrator_flow.py`

- [ ] **Step 1: Write end-to-end lifecycle test**

In `tmp_path` fake repo:

1. Register repo.
2. Open WorkRoom.
3. Build ContextPacket.
4. Open manual AgentSession.
5. Record EvidencePacket.
6. Approve DecisionRecord.
7. Close WorkRoom.
8. Re-load files from `.aiwg` and assert state persists.

- [ ] **Step 2: Implement orchestrator runtime**

Keep it small:

- no real external provider yet,
- no autonomous recruitment yet,
- no cross-repo export yet.

- [ ] **Step 3: Run lifecycle test**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests/test_agent_office_orchestrator_flow.py
```

Expected:

```text
passed
```

## Chunk 7: Integration and Verification

### Task 7: Run Full L2 and Existing Hardening Gates

**Files:**
- No new files unless failures expose real defects.

- [ ] **Step 1: Run agent office tests**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests/test_agent_office_*.py
```

Expected:

```text
all pass
```

- [ ] **Step 2: Run all L2 tests**

Run:

```bash
cd layers/l2_brain && uv run pytest -q tests
```

Expected:

```text
existing tests plus agent office tests pass
```

- [ ] **Step 3: Run industrial audit**

Run:

```bash
bash scripts/full_industrial_audit.sh
```

Expected:

```text
AUDITORÍA COMPLETADA CON ÉXITO
```

## Swarm Assignment

Use agents only after core contracts are clear:

- Worker A: models + storage.
- Worker B: SpecGraph + context builder.
- Worker C: provider adapter + orchestrator lifecycle.
- Worker D: verifier, reviews all outputs against design spec.

Workers must not edit files outside their ownership. The coordinator integrates and runs the full matrix.

## Promotion Criteria

MVP is ready when:

- WorkRoom lifecycle persists across process restarts.
- ContextPacket generation is deterministic.
- EvidencePacket and DecisionRecord link correctly.
- Repo-local `.aiwg` is used; no global memory leak.
- Provider adapter interface exists with a manual adapter.
- Tests prove the full loop without external network.

Real provider adapters are a follow-up plan after this MVP passes.

