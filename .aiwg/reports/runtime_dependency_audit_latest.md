# Runtime Dependency Audit Report
**Decision**: FAIL

## Monitored Dependencies
- **kuzu**: MISSING (Version: None)
- **pytest**: MISSING (Version: None)
- **yaml**: READY (Version: 6.0.1)
- **networkx**: MISSING (Version: None)
- **numpy**: MISSING (Version: None)
- **pydantic**: READY (Version: 2.12.5)
- **fastapi**: MISSING (Version: None)
- **typer**: MISSING (Version: None)
- **rich**: READY (Version: installed)
- **click**: READY (Version: 8.1.6)

## Missing Dependencies
- kuzu
- pytest
- networkx
- numpy
- fastapi
- typer

## Capability Classifications
- **Simulated**: kuzu_4dtes_persistence, daemon_persistent_runtime
- **Fallback**: real_semantic_embeddings, polyglot_build_test_runtime, token_usage_measurement
- **Dry-Run**: gateway_live_dispatch
- **Ready**: None

## Warnings / Remediation Triggers
- Kùzu Python package is missing; 4D-TES database persistence falls back to logical simulated mode.
- External embedding provider APIs are disabled. Memory Router uses deterministic fallback projection.
- Persistent background daemon is disabled. Life cycle runs in invocation-only advisory mode.
- MCP tool dispatch is human-gated (can_execute_now: false).
- Token Cost Ledger tracks estimates rather than active upstream API provider telemetry.
