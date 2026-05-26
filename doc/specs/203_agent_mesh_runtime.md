---
spec_id: 203_agent_mesh_runtime
title: Agent Mesh Runtime
status: ACTIVE
canonicality: canonical
artifact_type: spec
layer: dummie
created_by: codex_agent_mesh_runtime
last_verified_on: '2026-05-20'
claims:
- id: 203_agent_mesh_runtime-file-valid
  description: Spec file '203_agent_mesh_runtime.md' exists, parses valid YAML frontmatter,
    and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/203_agent_mesh_runtime.md').read().split('---')[1]); assert d,
    'empty frontmatter'"
  severity: critical
---
# Spec 203: Agent Mesh Runtime

## Purpose
Materialize DUMMIE Engine as a multi-CLI agent orchestrator instead of a single CLI facade.

## Scope
- Supported native agent profiles: `codex_cli`, `gemini_cli`, `antigravity`, `opencode`.
- Each agent has two input channels: `inbox`, `control`.
- Each agent has two output channels: `outbox`, `handoff`.
- The runtime generates per-agent boot bundles containing a system prompt and hook manifest.
- Initial lifecycle is file-backed and deterministic; automatic process spawn/close is reserved until supervision is verified.

## Runtime Behavior
1. `AgentMeshRuntime.bootstrap_mesh()` creates `.aiwg/agent_mesh/manifest.json`.
2. It creates one directory per agent under `.aiwg/agent_mesh/agents/`.
3. It writes channel files, `system_prompt.md`, and `hooks.json` for each agent.
4. `send_message()` records a message in the recipient inbox and sender outbox.
5. `dummie agent-mesh` exposes bootstrap, status, send, and read operations.

## Current State
- Implemented as a file-backed runtime in `dummie/agent_mesh.py`.
- Exposed through `dummie agent-mesh`.
- Automatic CLI process spawning is intentionally disabled until L0/L1 supervision is bound and tested.

## Physical Evidence
- `dummie/agent_mesh.py`
- `dummie/cli.py`
- `tests/test_agent_mesh_runtime.py`
- `tests/test_dummie_cli.py`

## Contract Invariants
- Every built-in CLI agent must have exactly two input channels and two output channels.
- Boot bundles must be generated from canonical runtime profiles, not ad hoc chat text.
- Mailbox artifacts under `.aiwg/agent_mesh/` are generated runtime state and must not be committed.
- Commit/push remains blocked unless required verification passes.

## Verification
- `uv run pytest -q tests/test_agent_mesh_runtime.py tests/test_dummie_cli.py`
- `python3 scripts/validate_specs_docs.py`

## Traceability
- Consumes provider detection from `dummie/providers.py`.
- Extends the session contract model under `.aiwg/session_contracts/`.
- Future spawn/close supervision must bind to L0/L1 process and gateway contracts before enabling autonomous lifecycle.
