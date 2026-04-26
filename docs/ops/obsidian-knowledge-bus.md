# Obsidian Knowledge Bus Operations

## Default Posture

The `obsidian` MCP server is registered in `dummie_agent_config.json` with `"disabled": true`.

Do not enable it until:

- Obsidian is running locally.
- The Obsidian Local REST API community plugin is installed and enabled.
- `OBSIDIAN_API_KEY` is supplied outside git.
- L1 MCP handshake tests pass.

## Sovereign Boundary

Obsidian is an external knowledge provider and human-readable mirror. It is not the operational source of truth. The 4D-TES remains authoritative after crystallization.

L2 must use provider-agnostic knowledge tools:

- `knowledge_search_context`
- `knowledge_get_artifact`
- `knowledge_ingest_artifact`
- `knowledge_export_decision_summary`
- `knowledge_export_lesson`
- `knowledge_export_session_summary`

L2 must not directly call `exec_remote_tool("obsidian", ...)`.

## Write Policy

Read operations are allowed through wrappers. Journal exports are append-only. Patch, overwrite, and delete require L3 intervention and human yield.

Never commit a real Obsidian API key.
