---
spec_id: 206_canonical_mcp_launcher_contract
title: Canonical MCP Launcher Contract
status: ACTIVE
layer: L1
last_verified_on: '2026-05-21'
claims:
- id: 206_canonical_mcp_launcher_contract-file-valid
  description: Spec file '206_canonical_mcp_launcher_contract.md' exists, parses valid
    YAML frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/206_canonical_mcp_launcher_contract.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# Spec 206: Canonical MCP Launcher Contract

## Purpose
Ensure every harness launches the same DUMMIE Brain MCP server, with one gateway inventory and one 4D-TES database path.

## Physical Evidence
- `scripts/mcp_wrapper.sh`
- `.agents/mcp_config.json`
- `/home/jorand/.config/opencode/opencode.jsonc`
- `scripts/dummie_orchestrator.py`
- `layers/l1_nervous/mcp_server.py`
- `dummie_gateway_config.json`
- `tests/test_mcp_launcher_contract.py`

## Contract
- The canonical MCP server is `layers/l1_nervous/mcp_server.py`.
- The canonical gateway inventory is `dummie_gateway_config.json`.
- The canonical Kùzu database path is `.aiwg/memory/kuzu_4d`.
- Launchers MUST use `scripts/mcp_wrapper.sh` so root, AIWG, Kùzu, and gateway config defaults are centralized.
- Launchers MUST NOT point to `/home/jorand/Escritorio`, per-layer `.venv/bin/python`, `loci.db`, or `~/.antigravity/mcp_config.registry.json`.
- OpenCode config is not hot-reloaded; after config edits, OpenCode must restart before the live tool handle reconnects.
- Verification harnesses MUST avoid launching multiple fresh MCP processes against `.aiwg/memory/kuzu_4d` in parallel, because Kùzu single-file locking can reject concurrent process opens.

## Verified Operations
```bash
PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/test_mcp_launcher_contract.py -q
```

Real STDIO checks performed:
- Project `.agents/mcp_config.json` launched and returned `CONFIG_PATH: /media/datasets/DUMMIE Engine/dummie_gateway_config.json`.
- Global OpenCode MCP command launched and returned `CONFIG_PATH: /media/datasets/DUMMIE Engine/dummie_gateway_config.json`.
- `local.brain_ping` returned `[L1-MCP] Engine Alive. Clock: 0`.
- A parallel harness run produced `Could not set lock on file : .aiwg/memory/kuzu_4d`; isolated sequential launcher checks passed, so this is a Kùzu concurrency boundary, not launcher misconfiguration.

## Handoff Note
The current running OpenCode session may still report `Not connected` until restarted, because MCP clients are created at startup.
