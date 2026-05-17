# Runtime Dependency Audit Report
**Decision**: PASS_WITH_WARNINGS

## Monitored Dependencies
- **kuzu**: READY (Version: 0.11.3)
- **pytest**: READY (Version: 9.0.3)
- **yaml**: READY (Version: 6.0.3)
- **networkx**: READY (Version: 3.6.1)
- **numpy**: READY (Version: 2.4.4)
- **pydantic**: READY (Version: 2.13.2)
- **fastapi**: READY (Version: 0.136.1)
- **typer**: READY (Version: 0.24.1)
- **rich**: READY (Version: installed)
- **click**: READY (Version: 8.3.2)

## Missing Dependencies
*None*

## Capability Classifications
- **Simulated**: daemon_persistent_runtime
- **Fallback**: real_semantic_embeddings, polyglot_build_test_runtime, token_usage_measurement
- **Dry-Run**: gateway_live_dispatch
- **Ready**: kuzu_4dtes_persistence

## Warnings / Remediation Triggers
- External embedding provider APIs are disabled. Memory Router uses deterministic fallback projection.
- Persistent background daemon is disabled. Life cycle runs in invocation-only advisory mode.
- MCP tool dispatch is human-gated (can_execute_now: false).
- Token Cost Ledger tracks estimates rather than active upstream API provider telemetry.
