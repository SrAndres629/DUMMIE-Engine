# Degraded Capability Registry Report
**Decision**: PASS_WITH_WARNINGS

## Registered Capabilities Status
### Kùzu DB 4D-TES Persistence (kuzu_4dtes_persistence)
- **Claimed Status**: READY
- **Actual Status**: READY
- **Reason**: Kùzu physical database persistence is available and writing.
- **Risk Level**: medium

### Real Semantic Vector Embeddings (real_semantic_embeddings)
- **Claimed Status**: READY
- **Actual Status**: FALLBACK
- **Reason**: External upstream embedding APIs are disabled. Local SHA256 deterministic mock routing is active.
- **Risk Level**: low
- **Blocked Actions**: semantic_similarity_search, high_dimensional_clustering

### Daemon Persistent Background Supervisor (daemon_persistent_runtime)
- **Claimed Status**: READY
- **Actual Status**: SIMULATED
- **Reason**: Sovereign background daemon loop is disabled. Operational lifecycle is invocation-only.
- **Risk Level**: high
- **Blocked Actions**: autonomous_background_heartbeat_loop, active_socket_bridge

### MCP Gateway Active Dispatcher (gateway_live_dispatch)
- **Claimed Status**: READY
- **Actual Status**: DRY_RUN_ONLY
- **Reason**: Daemon Gateway is invocation-only and enforces absolute manual review constraints.
- **Risk Level**: critical
- **Blocked Actions**: autonomous_tool_mutation_apply

### Polyglot Language Build & Test Orchestration (polyglot_build_test_runtime)
- **Claimed Status**: READY
- **Actual Status**: FALLBACK
- **Reason**: Language Probes detect languages but do not execute active builds or test runtimes dynamically.
- **Risk Level**: medium
- **Blocked Actions**: dynamic_otp_elixir_build, go_l1_binary_compile

### Upstream Token Usage Telemetry (token_usage_measurement)
- **Claimed Status**: READY
- **Actual Status**: FALLBACK
- **Reason**: Token Cost Ledger compiles static estimates rather than connecting to active provider usage counters.
- **Risk Level**: low
- **Blocked Actions**: upstream_cost_cap_enforcement

### Comprehensive Codebase Regression Testing (full_regression_suite)
- **Claimed Status**: READY
- **Actual Status**: DEGRADED
- **Reason**: Missing or orphan tests exist; the full regression run is not fully automated under single invoke.
- **Risk Level**: medium
- **Blocked Actions**: zero_regression_guarantees

### Dynamic Shadow Module Resolution (shadow_module_resolution)
- **Claimed Status**: READY
- **Actual Status**: SIMULATED
- **Reason**: Shadow modules are classified but not actively cleaned, archived, or resolved.
- **Risk Level**: low
- **Blocked Actions**: autonomous_shadow_module_pruning

### Active Spec and Runtime Validation (spec_runtime_mapping)
- **Claimed Status**: READY
- **Actual Status**: DEGRADED
- **Reason**: Spec validations fail due to physical evidence files that do not exist dynamically.
- **Risk Level**: medium
- **Blocked Actions**: automatic_spec_regression_blocks

### Physical upstream token measurement (context_actual_tokenizer)
- **Claimed Status**: READY
- **Actual Status**: FALLBACK
- **Reason**: Tokenizer uses simplified string-based cost models rather than active tiktoken/model libraries.
- **Risk Level**: low

