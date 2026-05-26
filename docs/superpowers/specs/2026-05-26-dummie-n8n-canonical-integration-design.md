# DUMMIE n8n Canonical Integration Design

> Date: 2026-05-26  
> Status: Implemented with canonical secrets and latency hardening in progress  
> Scope: Canonical source of truth for `OpenCode <-> DUMMIE <-> n8n` and `n8n -> DUMMIE`

## Intent

Establish one canonical architecture and one auditable source of truth for the local n8n integration with DUMMIE Engine and OpenCode.

This document is the design-level source of truth. Operational notes in `Escritorio/n8n/README-operativo.md` are subordinate summaries and must not diverge from this file.

## Canonical Source Of Truth

The canonical integration is defined by this spec plus the concrete runtime files listed below.

### Runtime truth files

- `/media/datasets/DUMMIE Engine/dummie_gateway_config.json`
- `/media/datasets/DUMMIE Engine/layers/l1_nervous/mcp_transport.py`
- `/media/datasets/DUMMIE Engine/layers/l1_nervous/mcp_server.py`
- `/media/datasets/DUMMIE Engine/layers/l1_nervous/mcp_server_runtime.py`
- `/media/datasets/DUMMIE Engine/layers/l1_nervous/capability_index.py`
- `/media/datasets/DUMMIE Engine/layers/l1_nervous/dummie_sdk/routing/strategies/exact_match.py`
- `/media/datasets/DUMMIE Engine/scripts/superpowers_mcp_proxy.py`
- `/media/datasets/DUMMIE Engine/scripts/mcp_wrapper.sh`
- `/media/datasets/DUMMIE Engine/scripts/run_dummie_mcp_http_gateway.sh`
- `/media/datasets/DUMMIE Engine/scripts/systemd/dummie-mcp-http.service`
- `/media/datasets/DUMMIE Engine/.agents/skills/n8n-expert/SKILL.md`
- `/home/jorand/.config/opencode/opencode.jsonc`
- `/home/jorand/Escritorio/n8n/compose.yaml`
- `/home/jorand/Escritorio/n8n/.env`
- `/home/jorand/Escritorio/n8n/.env.example`
- `/home/jorand/Escritorio/n8n/bin/n8n-wrapper`
- `/home/jorand/Escritorio/n8n/bin/n8n-with-stack`

## Goals

1. OpenCode must reach n8n through the existing `dummie-brain` MCP entry without introducing a parallel direct control plane.
2. DUMMIE must expose n8n capabilities through multiple MCP servers with clear roles.
3. n8n must be able to call DUMMIE through an HTTP MCP endpoint without breaking the existing stdio bridge.
4. Operational lifecycle must protect laptop resources: no forgotten `n8n` containers, no forgotten temporary HTTP gateways, no undocumented background services.
5. Secrets must stay out of tracked repo files and have one runtime source of truth.

## Non-Goals

1. Replacing the existing `dummie-brain` stdio bridge with HTTP.
2. Exposing n8n publicly outside loopback.
3. Storing the n8n API key in repo-tracked configuration.

## Canonical Topology

### OpenCode to n8n

```text
OpenCode CLI / session
  -> dummie-brain (stdio MCP)
  -> scripts/mcp_wrapper.sh loads /home/jorand/Escritorio/n8n/.env
  -> DUMMIE MCPProxyManager
  -> n8n / n8n_api / n8n_lint MCP sidecars
  -> local n8n API at http://127.0.0.1:5678
```

### n8n to DUMMIE

```text
n8n workflow / MCP Client / MCP Client Tool
  -> http://host.docker.internal:8765/mcp
  -> scripts/run_dummie_mcp_http_gateway.sh
  -> DUMMIE MCP gateway in streamable-http mode
  -> dummie_* / metagateway_* tools
```

## Secrets Single Source Of Truth

The canonical runtime source of truth for `N8N_API_URL`, `N8N_BASE_URL`, and `N8N_API_KEY` is:

- `/home/jorand/Escritorio/n8n/.env`

Propagation chain:

```text
/home/jorand/Escritorio/n8n/.env
  -> DUMMIE_N8N_ENV_FILE
  -> scripts/mcp_wrapper.sh
  -> dummie-brain process environment
  -> ${N8N_*} expansion in dummie_gateway_config.json
  -> n8n / n8n_api / n8n_lint sidecars
```

`~/.config/opencode/opencode.jsonc` is no longer the secret store. It only declares the runtime pointer `DUMMIE_N8N_ENV_FILE` so OpenCode and DUMMIE agree on the same source.

## MCP Server Roles

### `n8n`

Primary bridge for node knowledge, templates, validation, and main workflow operations.

- Package: `n8n-mcp`
- Transport: stdio sidecar
- Auth env: `N8N_API_URL`, `N8N_API_KEY`
- Extra constraint: `WEBHOOK_SECURITY_MODE=moderate`

### `n8n_api`

Full-surface API bridge for resources that the primary server does not cover deeply.

- Package: `@nextoolsolutions/mcp-n8n`
- Transport: stdio sidecar
- Auth env: `N8N_BASE_URL`, `N8N_API_KEY`
- Main value: workflows, executions, tags, credentials, users, variables, projects, Data Tables

### `n8n_lint`

Read-only diagnostic and workflow-quality bridge.

- Package: `@automatelab/n8n-mcp`
- Transport: stdio sidecar
- Auth env: `N8N_API_URL`, `N8N_API_KEY`
- Policy env: `N8N_MCP_READ_ONLY=1`

## Routing And Capability Surface

The canonical capability category for this domain is `workflow_automation`.

Required behaviors:

1. Local skills mentioning `n8n`, `workflow`, `webhook`, or automation concepts must index into `workflow_automation`.
2. Remote MCP servers with `capability_class == "workflow_automation"` must surface under that category.
3. Exact-match routing for `n8n`, `workflow`, and `webhook` requests must resolve intentionally to the `automation` domain instead of accidentally falling into generic shell handling.

## Skill Surface

`scripts/superpowers_mcp_proxy.py` must load both:

- Superpowers skills from `~/.agents/skills/superpowers`
- DUMMIE-local skills from `${DUMMIE_ROOT}/.agents/skills`

The local canonical skill for this integration is:

- `/media/datasets/DUMMIE Engine/.agents/skills/n8n-expert/SKILL.md`

Its role is operational guidance, not hidden state. The executable truth still lives in the runtime files above.

## Lifecycle And Hardware Discipline

### Rule 1: Interactive use

Humans use `n8n` / `bin/n8n-wrapper` and close it with `Ctrl+C`.

### Rule 2: Non-interactive agent use

Agents must not rely on `Ctrl+C`. They use `bin/n8n-with-stack <command...>` so startup and cleanup are paired in one process with `trap`-based teardown.

### Rule 3: Temporary HTTP gateway verification

Any ad hoc DUMMIE HTTP gateway process started for verification must be run in a bounded process scope and explicitly waited on or killed before the verification finishes.

### Rule 4: Idle Docker

If no containers remain running after an agent-managed verification and the agent started Docker, Docker should be stopped again.

## Secrets Policy

Secrets are runtime-only and must not be written into repo-tracked files.

- Allowed secret source: `/home/jorand/Escritorio/n8n/.env`
- Allowed runtime pointer: `~/.config/opencode/opencode.jsonc` via `DUMMIE_N8N_ENV_FILE`
- Not allowed: `dummie_gateway_config.json`, `compose.yaml`, `.env.example`, committed docs, test fixtures, hardcoded secrets in wrapper scripts

`.env` must be excluded from Git by `/home/jorand/Escritorio/n8n/.gitignore`.

## Discovery Semantics And Latency

### Root cause of the timeout

The production timeout was not caused by the `n8n` MCP sidecars themselves. The verified root causes were:

1. `dummie_discover_capabilities(query != "")` was falling into the metacognitive/LLM/research path because `IntentClassifier` did not recognize `n8n`, `workflow`, or `webhook` as an explicit automation domain.
2. Remote capability indexing had an incorrect `await` against a synchronous registry tool lookup, so remote MCP tool metadata was silently skipped.
3. The outer OpenCode runtime budget is lower than the inner `dummie-brain` process budget, so expensive fallback reasoning surfaced as client-side `MCP error -32001: Request timed out` before the inner process necessarily finished.

### Canonical latency strategy

The canonical fix must preserve the full metacognitive path for ambiguous or novel work while making routine n8n operations deterministic and fast.

Required strategy:

1. Keep the exact-match automation intent rules for `n8n`, `workflow`, `webhook`, and automation verbs.
2. Build and reuse a cached capability index for routine discovery instead of rebuilding the full index on every call.
3. Invalidate that cache when the live MCP server configuration or indexed skill files change.
4. Keep `MetacognitiveReasoner` as the fallback path only when the deterministic exact/cached path does not produce a valid match.
5. Prefer targeted queries such as `dummie_discover_capabilities(query="n8n")` and `dummie_analyze_capability(...)` for normal operation; reserve full inventory listing for diagnostics.

The canonical solution is therefore not to degrade intelligence, disable the router, or hardcode a tool path. It is to add a fast deterministic lane ahead of the expensive reasoning lane.

## Verification Requirements

Fresh evidence is required for each of these claims:

1. Targeted tests for MCP transport, routing, skill loading, and HTTP runtime mode.
2. `n8n` health endpoint reachable while stack is up.
3. Real MCP tool discovery against `n8n`, `n8n_api`, and `n8n_lint`.
4. Real HTTP reachability from inside the `n8n` container to the DUMMIE MCP endpoint.
5. Cleanup confirmation that no `n8n` containers remain active after non-interactive verification.

## Current Implemented State

Implemented:

- Multi-server `n8n` MCP topology in DUMMIE.
- DUMMIE local skill loading over the skill proxy.
- `n8n-expert` local skill.
- Intent and capability surfacing for workflow automation.
- HTTP-capable DUMMIE MCP gateway with launcher and optional systemd unit.
- Container-to-host connectivity path for `n8n -> DUMMIE`.
- Canonical secret loading from `/home/jorand/Escritorio/n8n/.env` through `scripts/mcp_wrapper.sh`.
- Cached capability indexing with explicit invalidation inputs for repeated discovery calls.

Still not closed as fully canonical until continuously maintained:

- This spec must be kept aligned when runtime files change.
- A production verification record should be refreshed after significant integration changes.

## Traceability Matrix

| Requirement | Runtime file(s) | Verification path |
|---|---|---|
| OpenCode reaches n8n through DUMMIE | `~/.config/opencode/opencode.jsonc`, `scripts/mcp_wrapper.sh`, `/home/jorand/Escritorio/n8n/.env`, `dummie_gateway_config.json` | capability discovery + remote MCP tool calls |
| MCP sidecars receive env correctly | `layers/l1_nervous/mcp_transport.py` | `layers/l1_nervous/tests/test_mcp_transport_env.py` |
| Wrapper loads canonical secrets env | `scripts/mcp_wrapper.sh`, `/home/jorand/Escritorio/n8n/.env` | `tests/test_mcp_wrapper_env_file.py` |
| n8n queries route intentionally | `exact_match.py`, `capability_index.py` | `layers/l1_nervous/tests/test_n8n_routing_and_capabilities.py` |
| Discovery reuses a deterministic cached index | `layers/l1_nervous/discovery_indexing.py`, `layers/l1_nervous/tools.py` | `layers/l1_nervous/tests/test_discovery_indexing.py` |
| DUMMIE local skills are MCP-loadable | `scripts/superpowers_mcp_proxy.py`, `.agents/skills/n8n-expert/SKILL.md` | `tests/test_superpowers_mcp_proxy.py` |
| DUMMIE can serve HTTP MCP | `mcp_server.py`, `mcp_server_runtime.py`, launcher, service unit | `layers/l1_nervous/tests/test_mcp_server_runtime.py` + live HTTP probe |
| Agent verifications do not leak `n8n` runtime | `bin/n8n-with-stack` | non-interactive verification run + `docker ps -a` |

## Canonical Operational Rule

If this spec conflicts with `README-operativo.md`, the spec wins and the README must be updated.
