# DUMMIE n8n Canonical Integration Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the existing DUMMIE+n8n integration to one canonical spec, make `/home/jorand/Escritorio/n8n/.env` the only secret source of truth, harden discovery latency without losing intelligence, and refresh production verification evidence.

**Architecture:** Keep the existing runtime topology, but move all `N8N_*` secret material to the n8n stack env file and have runtime wrappers load it canonically. For latency, keep the metacognitive router intact while adding a deterministic cached discovery lane that invalidates on config or skill changes.

**Tech Stack:** Bash, Docker Compose, systemd, Python 3.14, uv, MCP SDK, Markdown specs/plans.

---

### Files to Create/Modify
- Create: `docs/superpowers/specs/2026-05-26-dummie-n8n-canonical-integration-design.md`
- Create: `docs/superpowers/plans/2026-05-26-dummie-n8n-canonical-integration.md`
- Create: `/home/jorand/Escritorio/n8n/bin/n8n-with-stack`
- Create: `/home/jorand/Escritorio/n8n/.gitignore`
- Modify: `/home/jorand/Escritorio/n8n/README-operativo.md`
- Modify: `/home/jorand/Escritorio/n8n/.env`
- Modify: `/home/jorand/Escritorio/n8n/.env.example`
- Modify: `/home/jorand/.config/opencode/opencode.jsonc`
- Modify: `scripts/mcp_wrapper.sh`
- Modify: `scripts/run_dummie_mcp_http_gateway.sh`
- Modify: `scripts/systemd/dummie-mcp-http.service`
- Modify: `layers/l1_nervous/discovery_indexing.py`
- Modify: `layers/l1_nervous/tools.py`
- Test: `tests/test_mcp_wrapper_env_file.py`
- Test: `layers/l1_nervous/tests/test_discovery_indexing.py`

## Chunk 1: Canonical Documentation

### Task 1: Write the canonical integration spec

**Files:**
- Create: `docs/superpowers/specs/2026-05-26-dummie-n8n-canonical-integration-design.md`

- [ ] Step 1: Write the spec with one source-of-truth language and an explicit runtime file inventory.
- [ ] Step 2: Include topology for `OpenCode -> DUMMIE -> n8n` and `n8n -> DUMMIE`.
- [ ] Step 3: Include lifecycle rules for interactive and non-interactive use.
- [ ] Step 4: Include a traceability matrix mapping requirements to files and verification commands.

### Task 2: Downgrade README to an operational summary

**Files:**
- Modify: `/home/jorand/Escritorio/n8n/README-operativo.md`

- [ ] Step 1: Add a `Fuente de verdad canonica` section pointing to the new spec.
- [ ] Step 2: Add the non-interactive helper to the file inventory and usage guidance.
- [ ] Step 3: State clearly that the README is subordinate to the spec.

## Chunk 2: Non-Interactive Lifecycle Safety

### Task 3: Add a bounded stack helper for agent verifications

**Files:**
- Create: `/home/jorand/Escritorio/n8n/bin/n8n-with-stack`

- [ ] Step 1: Reuse the existing lifecycle logic from `bin/n8n-wrapper`.
- [ ] Step 2: Require a command argument instead of an infinite wait loop.
- [ ] Step 3: Add `trap cleanup EXIT INT TERM HUP`.
- [ ] Step 4: Ensure cleanup always runs `docker compose down` if the helper started the stack.
- [ ] Step 5: If the helper started Docker and no other containers remain, stop `docker.socket` and `docker`.
- [ ] Step 6: Make the script executable.

### Task 4: Document the helper as the canonical agent path

**Files:**
- Modify: `/home/jorand/Escritorio/n8n/README-operativo.md`

- [ ] Step 1: Document `bin/n8n-with-stack -- <command>` style usage.
- [ ] Step 2: Explain why it exists: agents cannot rely on manual `Ctrl+C`.

## Chunk 3: Fresh Production Verification

### Task 5: Verify the bounded helper and stack cleanup

**Files:**
- Test: `/home/jorand/Escritorio/n8n/bin/n8n-with-stack`

- [ ] Step 1: Run `systemctl is-active docker` before verification and record the state.
- [ ] Step 2: Run a bounded verification command through `bin/n8n-with-stack` that proves `n8n` health.
- [ ] Step 3: After the command exits, run `docker ps -a` and `systemctl is-active docker` again.
- [ ] Step 4: Confirm no `n8n` container remains active after the helper exits.

### Task 6: Refresh real DUMMIE-to-n8n evidence

**Files:**
- Test: `dummie_gateway_config.json`, `~/.config/opencode/opencode.jsonc`

- [ ] Step 1: Bring `n8n` up through the bounded helper or another bounded process.
- [ ] Step 2: Run a fresh DUMMIE-side verification that discovers and/or calls `n8n`, `n8n_api`, and `n8n_lint`.
- [ ] Step 3: If possible in this harness, run an `opencode run ...` command that exercises the current OpenCode CLI path.
- [ ] Step 4: Record exactly what was verified versus what remains only partially verified.

## Chunk 4: Canonical Secrets And Discovery Latency

### Task 7: Make `.env` the only secret source of truth

**Files:**
- Create: `/home/jorand/Escritorio/n8n/.gitignore`
- Modify: `/home/jorand/Escritorio/n8n/.env`
- Modify: `/home/jorand/Escritorio/n8n/.env.example`
- Modify: `/home/jorand/.config/opencode/opencode.jsonc`
- Modify: `scripts/mcp_wrapper.sh`
- Modify: `scripts/run_dummie_mcp_http_gateway.sh`
- Modify: `scripts/systemd/dummie-mcp-http.service`
- Test: `tests/test_mcp_wrapper_env_file.py`

- [ ] Step 1: Write a failing test proving `scripts/mcp_wrapper.sh` loads `N8N_*` values from an env file.
- [ ] Step 2: Run that test and verify it fails for the expected reason.
- [ ] Step 3: Add `.gitignore` rules so `.env` stays out of Git while `.env.example` remains tracked.
- [ ] Step 4: Add `N8N_API_URL`, `N8N_BASE_URL`, and `N8N_API_KEY` to `/home/jorand/Escritorio/n8n/.env` and placeholders to `.env.example`.
- [ ] Step 5: Update `~/.config/opencode/opencode.jsonc` to stop storing the secret directly and instead point to the env file via `DUMMIE_N8N_ENV_FILE`.
- [ ] Step 6: Update the DUMMIE wrappers and HTTP service path so they load the same env file canonically.
- [ ] Step 7: Re-run `tests/test_mcp_wrapper_env_file.py` and verify it passes.

### Task 8: Add deterministic cached discovery without removing metacognitive fallback

**Files:**
- Modify: `layers/l1_nervous/discovery_indexing.py`
- Modify: `layers/l1_nervous/tools.py`
- Test: `layers/l1_nervous/tests/test_discovery_indexing.py`

- [ ] Step 1: Write a failing test that proves repeated discovery can reuse a cached index until the config signature changes.
- [ ] Step 2: Run that test and verify it fails for the expected missing cache behavior.
- [ ] Step 3: Implement a canonical cache keyed by local-tool signature, remote server config signature, and skill-file mtimes.
- [ ] Step 4: Make `dummie_discover_capabilities` use that cache rather than rebuilding the full index every time.
- [ ] Step 5: Keep `MetacognitiveReasoner` untouched as the fallback path when exact/cached matching misses.
- [ ] Step 6: Re-run `layers/l1_nervous/tests/test_discovery_indexing.py` and verify it passes.

## Chunk 5: Completion Gate

### Task 9: Report completion with evidence only

**Files:**
- None

- [ ] Step 1: Re-run the exact verification commands used to justify the final claims.
- [ ] Step 2: Summarize active risks or unverified surfaces plainly.
- [ ] Step 3: Do not claim full closure if any route remains untested.
