# Multi-Repo Provider Agent Office Design

## Purpose

Design a multi-repository, multi-provider agent office where temporary AI sessions can collaborate like a software engineering team while preserving repo-local memory, specs, evidence, and context boundaries.

The system must give DUMMIE the metacognitive behavior the user wants: agents do not merely execute tasks; they question each other, verify claims, preserve useful context, and close sessions without losing the essential trace.

## Core Thesis

The agent is not the unit of truth. The **WorkRoom** is.

Agents are temporary workers. Providers are replaceable compute surfaces. The durable system is:

- repo-local 4D memory,
- repo-local specs and graph,
- explicit context packets,
- explicit evidence packets,
- orchestrated review loops,
- auditable decisions.

## Design Principles

1. **Repo memory is isolated**
   - Every repository owns its own `.aiwg` runtime.
   - No private repo memory is shared with another repo unless an explicit cross-repo context export is created.

2. **Global orchestration, local truth**
   - A global control plane can discover repos and open sessions.
   - The repo runtime decides which specs, memories, files, and constraints apply.

3. **Sessions are disposable**
   - External provider sessions can be opened and closed freely.
   - Continuity lives in 4D memory, WorkRooms, decisions, and evidence packets.

4. **Claims are not facts**
   - Any important agent claim must become an evidence packet.
   - A verifier or orchestrator must validate it against code, tests, docs, or memory before promotion.

5. **Context is leased, not dumped**
   - Agents receive minimal context packets scoped to their role and task.
   - Long conversation history is replaced by curated repo memory and task-specific retrieval.

6. **Roles define authority**
   - A researcher can investigate but not edit.
   - An implementer can edit only within assigned ownership.
   - A verifier can reject claims but not silently patch.
   - The orchestrator approves or reopens work.

7. **Providers are adapters**
   - Codex, Gemini, Claude, local models, and future providers must plug into the same session contract.
   - Provider-specific capabilities are metadata, not architecture.

## High-Level Architecture

```text
Global Control Plane
  ├── RepoRegistry
  ├── ProviderRegistry
  ├── RoleRegistry
  ├── ModelRoutingPolicy
  ├── SessionLifecycleManager
  └── CrossRepoExportPolicy

Per-Repo Runtime
  ├── .aiwg/memory/              repo-local 4D memory
  ├── .aiwg/workrooms/           durable task rooms
  ├── .aiwg/agents/              session manifests and role assignments
  ├── .aiwg/evidence/            claims, command output, diffs, reviews
  ├── .aiwg/context-packets/     scoped task context
  ├── .aiwg/provider-sessions/   external session metadata
  ├── doc/specs/                 repo-local specs
  └── SpecGraph Runtime          file/spec/rule/memory graph
```

## Main Runtime Objects

### RepoManifest

Describes a repository known to the global orchestrator.

```json
{
  "repo_id": "dummie-engine",
  "root": "/home/jorand/Escritorio/DUMMIE Engine",
  "memory_root": ".aiwg",
  "specs_root": "doc/specs",
  "trust_level": "private",
  "allowed_providers": ["codex", "gemini"],
  "default_orchestrator_model": "codex-5.5"
}
```

### WorkRoom

The durable unit of collaboration.

```json
{
  "workroom_id": "wr_20260425_orchestration_runtime",
  "repo_id": "dummie-engine",
  "objective": "Harden L2-L5 orchestration and introduce SpecGraph runtime",
  "status": "OPEN",
  "affected_paths": [
    "layers/l2_brain/**",
    "layers/l5_muscle/**",
    "doc/specs/**"
  ],
  "related_specs": [
    "doc/specs/02_memory_engine_4d_tes.md",
    "doc/specs/41_semantic_fabric_indexer.md"
  ],
  "agents": [],
  "decisions": [],
  "evidence": [],
  "created_at": "2026-04-25T00:00:00Z"
}
```

### AgentSession

A temporary worker session.

```json
{
  "session_id": "sess_01",
  "repo_id": "dummie-engine",
  "workroom_id": "wr_20260425_orchestration_runtime",
  "role": "contradictor",
  "provider": "gemini",
  "model": "gemini-flash",
  "can_edit": false,
  "allowed_paths": [
    "layers/l2_brain/**",
    "layers/l5_muscle/**",
    "doc/specs/**"
  ],
  "context_packet_id": "ctx_01",
  "expected_output": "evidence_review",
  "status": "OPEN"
}
```

### ContextPacket

The scoped context leased to an agent.

```json
{
  "context_packet_id": "ctx_01",
  "repo_id": "dummie-engine",
  "workroom_id": "wr_20260425_orchestration_runtime",
  "role": "researcher",
  "task": "Find the lowest-friction path to make real daemon-to-L5 execution pass.",
  "constraints": [
    "Do not edit files",
    "Prefer evidence from code and tests",
    "Flag assumptions explicitly"
  ],
  "files": [
    "layers/l2_brain/daemon.py",
    "layers/l5_muscle/mcp_driver.py",
    "layers/l2_brain/tests/test_daemon_hierarchical_planner.py"
  ],
  "specs": [
    "doc/specs/05_orchestration_stack_and_glue.md",
    "doc/specs/41_semantic_fabric_indexer.md"
  ],
  "memory_refs": [],
  "output_schema": "agent_research_report_v1"
}
```

### EvidencePacket

Evidence returned by an agent or command.

```json
{
  "evidence_id": "ev_01",
  "repo_id": "dummie-engine",
  "workroom_id": "wr_20260425_orchestration_runtime",
  "producer_session_id": "sess_01",
  "claim": "The daemon cannot dispatch through the real L5 driver because MCPDriver lacks execute().",
  "evidence": [
    "layers/l2_brain/daemon.py:115 calls self.muscle.execute(...)",
    "layers/l5_muscle/mcp_driver.py:14 defines send_command(...)",
    "smoke output: 'MCPDriver' object has no attribute 'execute'"
  ],
  "confidence": 0.91,
  "verification_status": "PENDING"
}
```

### DecisionRecord

An approved implementation decision.

```json
{
  "decision_id": "dec_01",
  "repo_id": "dummie-engine",
  "workroom_id": "wr_20260425_orchestration_runtime",
  "decision": "Add MCPDriver.execute() as the public executor contract and keep send_command() as transport detail.",
  "rationale": "L2 should depend on BaseExecutor behavior, not L5 transport naming.",
  "approved_by": "orchestrator",
  "evidence_ids": ["ev_01"],
  "status": "APPROVED"
}
```

## Agent Roles

### Orchestrator

Owns lifecycle and approval.

- Opens and closes WorkRooms.
- Creates ContextPackets.
- Assigns provider, model, and role.
- Reviews EvidencePackets.
- Approves decisions.
- Reopens work when verification fails.

### Planner

Turns objectives into route maps.

- Produces task decomposition.
- Defines ownership.
- Estimates friction and risk.
- Does not edit code.

### Researcher

Finds evidence.

- Reads code, docs, specs, memory.
- Produces hypotheses with citations.
- Does not edit code.

### Contradictor

Attacks weak assumptions.

- Reviews another agent's output.
- Searches for counterexamples.
- Requires physical evidence.
- Does not silently fix.

### CodeVerifier

Validates reality in the repo.

- Runs commands.
- Checks diffs.
- Confirms tests, builds, and imports.
- Produces evidence packets.

### SpecVerifier

Validates documentation and contracts.

- Checks spec frontmatter, feature/rules siblings, and traceability.
- Ensures implementation matches documented contract.

### Implementer

Edits code within ownership.

- Must receive explicit file ownership.
- Must produce tests before or with implementation.
- Must not alter unrelated files.

### Refactorer

Improves maintainability after behavior is proven.

- Works only after contract tests are green.
- Simplifies naming, boundaries, module layout.
- Must preserve behavior.

### PerformanceReviewer

Reviews runtime cost and scalability.

- Checks concurrency, latency, context size, provider cost.
- Recommends routing changes.

### Recruiter

Creates additional sessions when justified.

- Identifies missing expertise.
- Requests new agents with narrow scope.
- Cannot approve its own recruits' outputs.

## Provider Model Routing

Routing should be policy-driven:

```json
{
  "routing_rules": [
    {
      "role": "summarizer",
      "preferred_models": ["gemini-flash"],
      "reason": "Small outputs, low cost, high speed"
    },
    {
      "role": "contradictor",
      "preferred_models": ["gemini-flash", "codex-mini"],
      "reason": "Short adversarial review benefits from cheap diversity"
    },
    {
      "role": "architect",
      "preferred_models": ["codex-5.5", "gemini-3"],
      "reason": "High complexity and cross-module reasoning"
    },
    {
      "role": "implementer",
      "preferred_models": ["codex-5.5"],
      "reason": "Code editing and test integration require precision"
    }
  ]
}
```

The policy must support override per repo and per WorkRoom.

## Hybrid Tutor Flow

The 4D engine acts as tutor; the orchestrator acts as session manager.

```text
1. WorkRoom opens.
2. SpecGraph maps affected files to specs, rules, features, decisions, and memory.
3. 4D memory retrieves only relevant prior context.
4. Orchestrator creates ContextPacket.
5. Provider adapter opens AgentSession.
6. Agent returns output.
7. Output becomes EvidencePacket, not truth.
8. Contradictor or verifier reviews it.
9. Orchestrator approves, rejects, or assigns implementation.
10. Implementation produces diff and verification output.
11. Orchestrator closes WorkRoom.
12. 4D memory crystallizes decisions and lessons.
13. Provider sessions are closed.
```

## SpecGraph Runtime

SpecGraph is the repo-local map between code and documentation.

Minimum graph nodes:

- `File`
- `Directory`
- `Spec`
- `Rules`
- `Feature`
- `Layer`
- `Module`
- `Decision`
- `MemoryNode`
- `WorkRoom`
- `AgentSession`
- `EvidencePacket`

Minimum graph edges:

- `FILE_IN_LAYER`
- `FILE_IMPLEMENTS_SPEC`
- `SPEC_HAS_RULES`
- `SPEC_HAS_FEATURE`
- `FILE_REFERENCES_FILE`
- `DECISION_AFFECTS_FILE`
- `MEMORY_RELATED_TO_SPEC`
- `WORKROOM_TOUCHES_FILE`
- `EVIDENCE_SUPPORTS_DECISION`

First version can use deterministic path rules:

```text
layers/l2_brain/** -> layer L2 -> L2 specs
layers/l1_nervous/** -> layer L1 -> L1 specs
layers/l5_muscle/** -> layer L5 -> L5 specs
doc/specs/NN_name.md -> spec node
doc/specs/NN_name.rules.json -> rules node
doc/specs/NN_name.feature -> feature node
```

Later versions can add AST/LSP extraction.

## Prompt Injection

Prompt injection here means controlled system-context construction, not unsafe arbitrary prompt text.

Every agent system prompt should be assembled from:

- role contract,
- task objective,
- allowed operations,
- file ownership,
- relevant specs,
- relevant memory,
- output schema,
- verification obligations.

Example:

```text
You are the CodeVerifier for repo dummie-engine.
You cannot edit files.
Verify whether the implementer actually fixed the L2-L5 executor contract.
Relevant files:
- layers/l2_brain/daemon.py
- layers/l5_muscle/mcp_driver.py
- layers/l2_brain/tests/test_daemon_real_mcp_driver_contract.py
Required evidence:
- focused test output
- full L2 test output
- git diff summary
Return EvidencePacket JSON only.
```

## Cross-Repo Safety

Cross-repo work must be explicit.

Rules:

- A ContextPacket has exactly one primary `repo_id`.
- Cross-repo references must be declared as `external_refs`.
- External refs are summaries or public contract snippets, not raw private memory.
- A provider session cannot access two repo roots unless the WorkRoom is marked `cross_repo: true`.
- Repo-local memories never merge automatically.

## Storage Layout

Per repo:

```text
.aiwg/
  repo.json
  memory/
    loci.db
    decisions.jsonl
    lessons.jsonl
  workrooms/
    wr_<id>.json
  agents/
    sess_<id>.json
  context-packets/
    ctx_<id>.json
  evidence/
    ev_<id>.json
  provider-sessions/
    provider_<id>.json
  indexes/
    specgraph.json
```

Global:

```text
~/.dummie/control-plane/
  repos.json
  providers.json
  role-registry.json
  routing-policy.json
```

The global control plane stores orchestration metadata only. Repo truth stays in each repo.

## MVP Scope

The first MVP should not spawn 30 agents. It should prove the loop with two to four sessions:

1. Open WorkRoom for a known repo.
2. Build a path-based SpecGraph.
3. Generate a ContextPacket for one task.
4. Run a Researcher session.
5. Run a Contradictor or CodeVerifier session against the Researcher output.
6. Approve a DecisionRecord.
7. Close WorkRoom and crystallize memory.

Provider adapters can start with local/manual execution and then add Codex/Gemini adapters.

## Non-Goals for MVP

- No autonomous broad repo rewrites.
- No global shared memory across repos.
- No full AST language server.
- No automatic provider account management.
- No arbitrary agent self-recruitment without orchestrator approval.
- No hidden background edits.

## Acceptance Criteria

The design is implemented enough for MVP when:

- A repo can register itself with a `repo_id`.
- A WorkRoom can be opened and closed.
- A ContextPacket can be generated from file paths and specs.
- An AgentSession manifest can be created for at least one provider adapter.
- An EvidencePacket can be recorded and verified.
- A DecisionRecord can be approved and linked to evidence.
- Repo-local `.aiwg` memory is not mixed with another repo.
- The process works after closing and reopening sessions.

## Risks

- **Context leakage across repos:** mitigate with repo-scoped packets and explicit external refs.
- **Provider hallucination:** mitigate with evidence packets and verifier roles.
- **Agent sprawl:** mitigate with WorkRoom limits and recruiter approval.
- **Overengineering:** start with JSON/JSONL contracts and path-based SpecGraph.
- **Spec drift:** require SpecVerifier in promotion gates.
- **Maintenance burden:** keep adapters thin and contracts stable.

## Recommended First Implementation Order

1. Define JSON schemas/models for RepoManifest, WorkRoom, AgentSession, ContextPacket, EvidencePacket, DecisionRecord.
2. Implement repo-local storage.
3. Implement path-based SpecGraph.
4. Implement ContextPacket builder.
5. Implement provider adapter interface with one local/manual adapter.
6. Implement verifier loop.
7. Add Codex/Gemini adapters after the contracts are stable.

