# DUMMIE Engine Roadmap Ledger to Pack 6.1

*Generated at: 2026-05-18T22:30:00Z*

## Truth Reconciliation
- **HEAD of main**: `06478a1`
- **Pack 2.2 Status**: MERGED (`f0345c8`)
- **Pack 2.3 Status**: MERGED (`c1f7de4`)
- **Batch 5 Status**: MERGED (`06478a1`)
- **Current Target**: **Pack 2.4 - Superficial Tests Upgrade**

## Upcoming Packs

### Pack 2.4 - Superficial Tests Upgrade
- **Objective**: Convert import-only/assert-free tests into behavioral tests.
- **Status**: PENDING
- **Batch Size**: 8-15 tests.
- **Criteria**: `superficial_tests` drops; each test validates a contract/invariant.
- **Preconditions**: Pack 2.3 merged. Main clean.

### Pack 2.5 - UNKNOWN Classification Batch
- **Objective**: Classify UNKNOWN by fan-in/importance.
- **Status**: PENDING
- **Batch Size**: 40-80 files.
- **Criteria**: UNKNOWN count drops significantly; no hiding debt as legacy without evidence.

### Pack 2.6 - Orphan Tests + Frozen Scripts
- **Objective**: Resolve 3 `ORPHAN_TEST_CANDIDATE` and critical frozen scripts.
- **Status**: PENDING
- **Criteria**: orphan tests = 0 or justified; scripts have owner/status.

### Pack 2.7 - CI + Freshness Gates
- **Objective**: Automate validations (specs_docs, structural triage, mesh tests, freshness).
- **Status**: PENDING
- **Criteria**: Minimal CI active.

### Pack 2.8 - Repo Health Recalibration
- **Objective**: Recalculate structural health.
- **Status**: PENDING
- **Criteria**: CRITICAL=0, HIGH<20, SHADOW<20, UNKNOWN<30, ORPHAN=0, repo_health_status=PASS_WITH_WARNINGS.

### Pack 3.0 - Real TEXT_FAST Embedding Provider
- **Objective**: Partially exit fallback_hash_384.
- **Status**: PENDING
- **Criteria**: vector_space real active; fallback preserved; no unmanaged runtime downloads.

### Pack 3.1 - Reranker Real or Hybrid+
- **Objective**: Improve evidence ranking.
- **Status**: PENDING
- **Criteria**: Real offline reranker or audited hybrid with metrics.

### Pack 3.2 - CODE Embedding Provider
- **Objective**: Separate code search from text search.
- **Status**: PENDING
- **Criteria**: Code vector_space active; spaces not mixed.

### Pack 3.3 - Direct Spec Linkage Engine
- **Objective**: Increase `direct_spec_hit_rate` and reduce scoped-only links.
- **Status**: PENDING
- **Criteria**: More precise module-spec linkages.

### Pack 4.0 - ModelCapability Registry
- **Objective**: Formalize specialist model classes.
- **Status**: PENDING
- **Criteria**: Contractual registry, no massive implementation.

### Pack 4.1 - ModelRouter v2
- **Objective**: Route by `capability_chain`.
- **Status**: PENDING
- **Criteria**: task + modality + risk + budget + context_quality -> capability_chain.

### Pack 4.2 - Guardrail Layer
- **Objective**: Security before actions.
- **Status**: PENDING
- **Criteria**: secrets/PII/destructive-action checks active.

### Pack 4.3 - Function Calling Contract Layer
- **Objective**: Tool calls with JSON schema and error taxonomy.
- **Status**: PENDING
- **Criteria**: Validated tool calls.

### Pack 4.4 - Code LLM Integration
- **Objective**: Local/cloud code model adapter with sandbox/test gate.
- **Status**: PENDING
- **Criteria**: No patches accepted without a test gate.

### Pack 5.0 - Document Intelligence / LangExtract Adapter
- **Objective**: Grounded extraction for long documents.
- **Status**: PENDING
- **Criteria**: JSON with source spans.

### Pack 5.1 - Runtime Context Compression Policy
- **Objective**: Prepare KV cache/TurboQuant without overclaim.
- **Status**: PENDING
- **Criteria**: Policy detects real backend; no fake promises.

### Pack 5.2 - Local Inference Backend Registry
- **Objective**: Register Ollama/llama.cpp/MLX if present.
- **Status**: PENDING
- **Criteria**: Health check and model inventory without automatic download.

### Pack 6.0 - Operational CI Full Gate
- **Objective**: Complete quality pipeline.
- **Status**: PENDING
- **Criteria**: main protected by tests, specs, hardening, freshness, secret scan.

### Pack 6.1 - Minimal Golden Path
- **Objective**: Demonstrate full operational flow.
- **Status**: PENDING
- **Criteria**: Reproducible end-to-end case (query -> retrieval -> ... -> memory).
