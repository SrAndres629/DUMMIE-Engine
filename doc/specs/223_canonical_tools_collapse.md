---
status: SUPERSEDED
claims:
- id: canonical_flag_exists
  description: DUMMIE_CANONICAL_ONLY implementado en tools.py
  severity: critical
- id: dummie_admin_registered
  description: dummie_admin registrado como tool MCP
  severity: critical
implementations:
- file: layers/l1_nervous/tools.py
  constant: DUMMIE_CANONICAL_MODE
  type: primary
superseded_by: doc/architecture/SMART_METAGATEWAY_ARCHITECTURE.md
---

# Collapse 9 tools → 2 canonical tools

**Date:** 2026-05-26
**Phase:** G1
**Requires reboot:** No
**Depends on:** Nothing
**Files modified:** `layers/l1_nervous/tools.py`

## Problem

9 MCP tools exposed to agent: `dummie_discover_capabilities`, `dummie_report_config_path`, `dummie_analyze_capability`, `dummie_execute_capability`, `dummie_install_mcp`, `dummie_self_program`, `metagateway_discover`, `metagateway_cot_reason`, `dummie_process`.

Each consumes ~80-120 tokens in the agent's context window. Total: ~900 tokens of context wasted on tool schemas before any reasoning begins.

The agent must also reason about which of 9 tools to use, when `dummie_process` handles 95% of cases.

## Design

### Target: 2 tools

| Tool | Purpose | Absorbs |
|------|---------|---------|
| `dummie_process` | Main entry — intent → route → execute | 5 old tools |
| `dummie_admin` | Install, config, codegen, status | 3 old tools |

### Collapse map

| Old tool | New location |
|----------|-------------|
| `dummie_discover_capabilities` | `dummie_process(mode="discover")` |
| `metagateway_discover` | `dummie_process(mode="discover")` |
| `metagateway_cot_reason` | `dummie_process(mode="cot_reason")` |
| `dummie_analyze_capability` | `dummie_process(mode="analyze", target="...")` |
| `dummie_execute_capability` | `dummie_process(mode="execute", target="server.tool", arguments={...})` |
| `dummie_report_config_path` | `dummie_admin(action="report_config")` |
| `dummie_install_mcp` | `dummie_admin(action="install_mcp", ...)` |
| `dummie_self_program` | `dummie_admin(action="self_program", mission="...")` |

### Feature flag

```python
CANONICAL_ONLY = os.environ.get("DUMMIE_CANONICAL_ONLY", "").lower() in ("1", "true", "yes")
```

When `CANONICAL_ONLY=false` (default): all 9 tools registered (backward compat).
When `CANONICAL_ONLY=true`: only `dummie_process` + `dummie_admin` registered. Old tools still exist internally on `internal_mcp`.

### Implementation in register_tools()

```python
def register_tools(mcp, get_orchestrator, get_proxy, root_dir):
    CANONICAL = os.environ.get("DUMMIE_CANONICAL_ONLY", "").lower() in ("1", "true", "yes")
    
    # Old tools registered only if not canonical
    if not CANONICAL:
        dummie_discover_capabilities = ...  # registered
        dummie_report_config_path = ...     # registered
        dummie_analyze_capability = ...     # registered
        dummie_execute_capability = ...     # registered
        dummie_install_mcp = ...            # registered
        dummie_self_program = ...           # registered
        metagateway_discover = ...          # registered
        metagateway_cot_reason = ...        # registered
    
    # Always registered
    dummie_process = ...                    # registered
    dummie_admin = ...                      # registered
```

### dummie_admin implementation

```python
@mcp.tool()
async def dummie_admin(action: str, **kwargs) -> str:
    """
    Administrative operations for the DUMMIE Engine.
    
    Actions:
      - "report_config": Show MCP config path
      - "install_mcp": Install a new MCP server (needs server_name, command, args)
      - "self_program": Generate code for a technical mission (needs mission)
      - "status": Show gateway health and connected servers
    """
    if action == "report_config":
        _, proxy_manager = setup_internal()
        return f"CONFIG_PATH: {proxy_manager.config_path}"
    
    if action == "install_mcp":
        server_name = kwargs.get("server_name")
        command = kwargs.get("command")
        args = kwargs.get("args", [])
        # delegate to existing dummie_install_mcp logic
    
    if action == "self_program":
        mission = kwargs.get("mission")
        # delegate to existing dummie_self_program logic
    
    if action == "status":
        # return gateway health summary
```

## Success criteria

| Metric | Before | After |
|--------|--------|-------|
| Tools exposed | 9 | 2 |
| Context tokens for schemas | ~900 | ~200 |
| Agent decision ("which tool?") | 9 options | 2 options |
| Old tools still accessible internally | N/A | Yes (via internal_mcp) |
| Backward compat | N/A | `CANONICAL_ONLY=false` restores 9 tools |