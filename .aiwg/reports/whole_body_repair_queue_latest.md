# Whole Body Repair Queue Report
**Decision**: `PASS`  

## Prioritized Repair Backlog
### 1. Integrate Kuzu Graph Sync and Loci.db Readback (Priority: `HIGH`)
- **Action ID**: `integrate_kuzu_graph_sync`
- **Body Part**: `memory`
- **Capability ID**: `kuzu_4dtes_persistence`
- **Action Type**: `wire`
- **Requires Human Approval**: `True`
- **Can Execute Now**: `False`
- **Recommended Agent**: `antigravity`
- **Verification Commands**: `['dummie-ctl kuzu-readback']`
### 2. Activate Local Embedding Model or Label Fallback Cosine Projections (Priority: `MEDIUM`)
- **Action ID**: `activate_local_embedding_model_or_label_fallback`
- **Body Part**: `memory`
- **Capability ID**: `real_semantic_embeddings`
- **Action Type**: `configure`
- **Requires Human Approval**: `False`
- **Can Execute Now**: `True`
- **Recommended Agent**: `local`
- **Verification Commands**: `['dummie-ctl embedding-activation']`
### 3. Wire Upstream Token Usage Dynamic Telemetry (Priority: `MEDIUM`)
- **Action ID**: `wire_upstream_token_usage_telemetry`
- **Body Part**: `metabolism`
- **Capability ID**: `token_usage_measurement`
- **Action Type**: `wire`
- **Requires Human Approval**: `True`
- **Can Execute Now**: `False`
- **Recommended Agent**: `codex`
- **Verification Commands**: `['dummie-ctl token-usage']`
### 4. Configure Polyglot Build and Test Lifecycle Orchestration (Priority: `MEDIUM`)
- **Action ID**: `configure_polyglot_build_test_lifecycle`
- **Body Part**: `polyglot_body`
- **Capability ID**: `polyglot_build_test_runtime`
- **Action Type**: `configure`
- **Requires Human Approval**: `True`
- **Can Execute Now**: `False`
- **Recommended Agent**: `gemini`
- **Verification Commands**: `['pytest layers/l2_brain/tests/']`
