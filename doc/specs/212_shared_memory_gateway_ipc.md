---
spec_id: 212_shared_memory_gateway_ipc
title: Shared Memory Gateway IPC
status: ACTIVE
layer: L1
last_verified_on: '2026-05-25'
claims:
- id: 212_shared_memory_gateway_ipc-file-valid
  description: Spec file '212_shared_memory_gateway_ipc.md' exists, parses valid YAML
    frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/212_shared_memory_gateway_ipc.md').read().split('---')[1]); assert
    d, 'empty frontmatter'"
  severity: critical
---
## Purpose
Optimize the IPC path between MetaGateway and sub-gateways (media:8081, code:8082, infra:8083, knowledge:8084, shell:8085) by replacing HTTP JSON serialization with shared memory (memfd) for large payloads. Currently each tool call serializes arguments as HTTP JSON over localhost, adding ~1-5ms of HTTP overhead per call.

## Current State
- MetaGateway → sub-gateway: `httpx.AsyncClient.post("http://localhost:{port}/call", json=...)` 
- Sub-gateway → MCP server: stdio subprocess
- Gateway readiness: filesystem `.ready` markers in `.aiwg/runtime/gateways/`
- No shared memory in the IPC chain

## Physical Evidence
- `metagateway.py:44-53` — HTTP POST to sub-gateways
- `base_gateway.py:52-56` — tool call via MCP stdio
- Gateway configs in `layers/l1_nervous/configs/`

## Contract Invariants
- **Zero-copy path**: Payloads >64KB must use memfd shared memory instead of HTTP JSON
- **Fallback**: HTTP remains the default for small payloads; memfd is an optimization, not a replacement
- **Isolation**: Shared memory pages must be sealed (F_SEAL_SHRINK, F_SEAL_SEAL) after writing
- **Idempotent**: Memfd transfer must be idempotent (receiver reads once, then unlinks)

## Verification
```bash
# Test: large payload goes through memfd
python3 -c "
from layers.l1_nervous.metagateway import MetaGateway
import asyncio
mg = MetaGateway()
# Large payload
payload = {'query': 'x' * 100000}
result = asyncio.run(mg.route_request(payload['query']))
print(f'Payload OK, confidence={result.get(\"confidence\")}')
"
ls -la /proc/$(pgrep -f metagateway)/fd/ 2>/dev/null | grep memfd
```

## Traceability
- Maps to: FDA-001 (revertible optimization)
- Source changes: `layers/l1_nervous/metagateway.py`, `layers/l1_nervous/gateway/base_gateway.py`
