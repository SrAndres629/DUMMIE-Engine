---
spec_id: DE-V2-CROSS-100
title: L0-L2 Cognitive Bridge via MCP STDIO
status: ACTIVE
layer: CROSS
last_verified_on: '2026-05-20'
priority: MANDATORY
version: 1.0.0
namespace: dummie.engine.cross
---

# L0(Go) → L2(Python) Cognitive Bridge

## Purpose
Enable the Go daemon (L0) to delegate cognitive operations to the Python cognitive layer (L2) via MCP STDIO transport, as specified in Spec 52 and Spec 44.

## Current State
Implemented and verified in production. Go daemon can invoke L2 cognitive capabilities on-demand.

## Physical Evidence
- `layers/l0_overseer/internal/orchestrator/cognitive_bridge.go` — Go MCP STDIO client
- `layers/l0_overseer/internal/orchestrator/daemon.go` — COGNITION command handler
- `layers/l1_nervous/mcp_server.py` — MCP STDIO server (DUMMIE-Brain-Gateway)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ L0: Go Daemon (dummied)                                     │
│   - Unix socket control interface                           │
│   - SPAWN_SWARM, PING, COGNITION commands                   │
│   - CognitiveBridge: MCP STDIO client                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ COGNITION command
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ MCP STDIO (on-demand subprocess)                            │
│   - uv run python -m layers.l1_nervous.mcp_server           │
│   - JSON-RPC 2.0 protocol                                   │
│   - Tools: dummie_discover_capabilities,                    │
│            dummie_execute_capability, local.brain_ping, etc │
└──────────────────────┬──────────────────────────────────────┘
                       │ Tool execution
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ L2: Python Cognitive Layer                                  │
│   - EmbeddingRouter (Spec 192)                              │
│   - ModelExecutor (Spec 200)                                │
│   - ToolSelector                                            │
│   - SkillRegistry                                           │
│   - 4D-TES Memory                                           │
└─────────────────────────────────────────────────────────────┘
```

## Contract Invariants
- **On-Demand**: MCP STDIO process is spawned per request, not persistent (Spec 52)
- **JSON-RPC 2.0**: Standard MCP protocol with initialize → notifications/initialized → tools/call
- **Timeout**: 30 seconds default, configurable per request
- **Cleanup**: MCP process is killed after response, no orphan processes
- **Error Propagation**: MCP errors are propagated to Go daemon caller
- **No Degradation**: Real MCP execution, no dry runs or simulations

## Commands

### PING
```json
{"type": "PING"}
```
Response: `{"status": "ok", "message": "PONG"}`

### COGNITION
```json
{
  "type": "COGNITION",
  "target": "local.brain_ping",
  "args": {}
}
```
Response:
```json
{
  "status": "ok",
  "result": {
    "success": true,
    "result": {"content": [...], "structuredContent": {...}},
    "latency_ms": 659.5
  }
}
```

## Verification
```bash
# 1. Start daemon
DUMMIE_ROOT=/path/to/root DUMMIE_AIWG_DIR=/path/to/.aiwg ./bin/dummied &

# 2. Test PING
echo '{"type": "PING"}' | nc -U .aiwg/sockets/dummied.sock

# 3. Test COGNITION (brain ping)
echo '{"type": "COGNITION", "target": "local.brain_ping", "args": {}}' | nc -U .aiwg/sockets/dummied.sock

# 4. Test COGNITION (discover capabilities)
echo '{"type": "COGNITION", "target": "dummie_discover_capabilities", "args": {"query": "memory"}}' | nc -U .aiwg/sockets/dummied.sock

# 5. Verify no orphan MCP processes
ps aux | grep mcp_server | grep -v grep
```

## Traceability
- **Spec 52**: MCP uses STDIO transport, launched on-demand
- **Spec 44**: Local reasoning gateway via dummie-brain MCP
- **Spec 50**: Daemon outcome carries model route metadata
- **ADR-001**: Polyglot architecture (L0=Go, L2=Python)
