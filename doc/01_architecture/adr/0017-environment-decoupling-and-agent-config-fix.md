---
spec_id: "DE-ADR-0017"
title: "Agent Configuration and Layer Decoupling"
status: "ACCEPTED"
version: "1.0.0"
layer: "L1"
namespace: "io.dummie.v2.adr"
authority: "SCRIBE"
tags: ["adr", "environment", "decoupling", "agent-config"]
---

# ADR-0017: Agent Configuration and Layer Decoupling

## Status
**ACCEPTED**

## Context
During the operational phase, two critical failures were identified:
1.  **Agent Inoperability:** The `overseer-meta` agent failed to load due to invalid tool names in its configuration (`.gemini/agents/overseer-meta.md`). Specifically, the sequential thinking tool was incorrectly referenced.
2.  **Circular Dependency & Environment Fragility:** The L1 (Nervous) adapter was disconnected because it shared a virtual environment with L2 (Brain), which contained broken absolute symlinks to external paths. This violated the principle of "Independent Gears".

## Decision
To ensure system resilience and compliance with the hexagonal architecture, the following actions were taken:

1.  **Configuration Correction:** Tool names in `.gemini/agents/overseer-meta.md` were updated to match the standard MCP naming convention: `mcp_sequentialthinking_sequentialthinking` and `run_shell_command`.
2.  **Environment Isolation:** A dedicated, isolated virtual environment was created at `layers/l1_nervous/.venv`. This decouples L1's execution environment from L2.
3.  **Dependency Updates:** Critical dependencies for L1 (`kuzu`, `mcp`, `pydantic`) were installed and pinned within this new environment.
4.  **Agent Config Synchronization:** The `dummie_agent_config.json` was updated to point to the new python interpreter in `layers/l1_nervous/.venv/bin/python`.

## Rationale
- **Resilience:** Decoupling ensures that failure in one layer's environment (e.g., L2's broken symlinks) does not bring down another layer (L1).
- **Correctness:** Using exact MCP tool names is mandatory for the orchestration engine to correctly bind capabilities to agents.
- **Sovereignty:** Each layer should manage its own dependencies to maintain the "Independent Gear" architecture.

## Consequences
- **Positive:** Increased system stability, easier debugging of layer-specific issues, and proper agent initialization.
- **Negative:** Slightly increased disk usage due to multiple virtual environments.
- **Maintenance:** Developers must ensure that each layer's `.venv` is maintained independently.

## [MSA] Sibling Components Requeridos
- **Executable Contract:** `0017-environment-decoupling-and-agent-config-fix.feature`
- **Machine Rules:** `0017-environment-decoupling-and-agent-config-fix.rules.json`
