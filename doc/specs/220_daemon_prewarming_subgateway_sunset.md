---
status: Approved
claims:
- id: prewarm_env_set
  description: DUMMIE_PREWARM configurada en .env
  severity: high
- id: sub_gateways_stopped
  description: 5 sub-gateways enmascarados sin procesos activos
  severity: critical
---

# Phase E+F: Daemon Pre-warming + Sub-gateway Sunset

**Date:** 2026-05-26  
**Phase:** E, F  
**Requires reboot:** No  
**Depends on:** Phase D (skill executor)  

## Phase E — Daemon Pre-warming

### 1. Purpose

Keep frequently-used MCP servers (filesystem, shell) warm to eliminate cold-start latency (1-5s per first tool call). Without pre-warming, the first `filesystem.read_text_file` or `shell.execute_command` call incurs a full subprocess spawn + MCP handshake.

### 2. Design

Add pre-warming logic to `MCPProxyManager.__init__()`. After initialization, spawn "hot" servers in the background.

```python
# mcp_proxy.py: MCPProxyManager.__init__
if os.environ.get("DUMMIE_PREWARM"):
    for server in os.environ["DUMMIE_PREWARM"].split(","):
        server = server.strip()
        if server in self.registry.servers:
            logger.info("Pre-warming server: %s", server)
            asyncio.create_task(self._ensure_ready(server))
```

Default: `DUMMIE_PREWARM=filesystem,shell` set in `.env`.

### 3. Implementation

- Add 5 lines to `mcp_proxy.py::__init__`
- Add `DUMMIE_PREWARM=filesystem,shell` to `.env`

### 4. Success criteria

| Metric | Before | After |
|--------|--------|-------|
| First `filesystem.read_text_file` call | 1-5s cold | <100ms warm |
| First `shell.execute_command` call | 1-5s cold | <100ms warm |
| Additional system resources | 0 | ~50MB (2 idle subprocesses) |

## Phase F — Sub-gateway Sunset

### 1. Purpose

Decommission the 5 HTTP sub-gateways (media, code, infra, knowledge, shell on ports 8081-8085) that were verified as NOT in the hot path. They run as systemd services consuming ~5MB each, 5 subprocesses total. The architecture analysis confirmed the primary path goes through `MCPProxyManager.call_tool()` via STDIO, not through the HTTP sub-gateways.

### 2. Design

Minimal, safe sunset:
1. Mask systemd services so they don't autostart on reboot
2. Keep all code files (gateway/*.py, config JSONs) — no deletion
3. If rollback needed: unmask services and restart

### 3. Implementation

```bash
systemctl mask dummie-gateway@media
systemctl mask dummie-gateway@code
systemctl mask dummie-gateway@infra
systemctl mask dummie-gateway@knowledge
systemctl mask dummie-gateway@shell
systemctl stop dummie-gateway@media dummie-gateway@code dummie-gateway@infra dummie-gateway@knowledge dummie-gateway@shell
```

### 4. Success criteria

| Metric | Before | After |
|--------|--------|-------|
| Running gateway processes | 10 (5 under systemd + 5 rogue) | 0 |
| Ports 8081-8085 occupied | Yes | No |
| Memory freed | 0 | ~25-50MB |
| Rollback capability | Immediate | `systemctl unmask` + `systemctl start` |

### 5. Files

| File | Action |
|------|--------|
| `layers/l1_nervous/mcp_proxy.py` | **Modify** — add pre-warming logic |
| `.env` | **Modify** — add `DUMMIE_PREWARM=filesystem,shell` |
| Systemd | **Modify** — mask 5 sub-gateway services |