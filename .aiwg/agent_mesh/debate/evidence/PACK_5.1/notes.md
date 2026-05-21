=== notes.md ===
# PACK_5.1: Eliminar 27 módulos flat_brain sin spec

## Initial plan
- 27 'orphan' modules identified with 0 flat_brain-specific imports
- LEGACY backup created first in flat_brain_LEGACY/

## Discovery during execution
- Only 10/27 are truly orphaned (0 imports ANYWHERE)
- 17/27 have live imports via _FlatBrainFallbackFinder (imported as layers.l2_brain.<mod>)
- These 17 were restored from LEGACY backup and are deferred to PACK_5.2

## Files deleted (10)
- causal_replay, entropy_governor, golden_path, lifecycle_integration_mapper
- metagateway_benchmark, prompt_preprocessor, sdd_governance
- sovereign_runtime_readiness, total_project_truth_scan, witness

## Files restored (17) - deferred to PACK_5.2
- ast_indexer, auto_evolution, branch_memory, entity_voice
- evolution_feedback_loop, expansion_policy, file_dossier_generator
- folder_dossier_generator, formal_bridge, freshness_ledger
- graph_sync_ledger, patch_transaction, patch_transaction_manager
- restart_integration_gate, stale_memory_detector, tool_opportunity_detector
- workbench_vault_runtime

## Verification results
- Import chain: OK (dummie.engine + layers.l2_brain)
- Tests: 5 passed (kuzu path hardening)
- Spec registry: 87 specs, 0 errors
- Production critical_failures: ollama_runtime, model_executor (pre-existing)

## Remaining flat_brain modules
- 187 modules in flat_brain/ (down from 230)
- 17 modules with live imports pending migration/restructuring (PACK_5.2)
- LEGACY backup preserved in flat_brain_LEGACY/ for safety
