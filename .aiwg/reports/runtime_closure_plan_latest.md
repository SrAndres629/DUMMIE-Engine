# Runtime Closure Plan Report
**Decision**: PASS_WITH_WARNINGS

## Actionable Repair Steps (Human Gated)
### Install Kùzu Python Bindings (install_kuzu_library)
- **Capability**: `kuzu_4dtes_persistence`
- **Action Type**: `install_dependency`
- **Priority**: CRITICAL
- **Can Execute Now**: `False`
- **Requires Human Approval**: `True`
- **Commands to Run**:
  - `.venv/bin/pip install kuzu==0.7.1`
- **Verification Commands**:
  - `.venv/bin/python -c 'import kuzu; print(kuzu.__version__)'`

### Configure Kùzu Database Directory (configure_kuzu_db_path)
- **Capability**: `kuzu_4dtes_persistence`
- **Action Type**: `configure_path`
- **Priority**: HIGH
- **Can Execute Now**: `False`
- **Requires Human Approval**: `True`
- **Commands to Run**:
  - `mkdir -p .aiwg/memory/loci.db`
- **Verification Commands**:
  - `test -d .aiwg/memory/loci.db`

### Verify Non-Destructive Kùzu DB Write/Readback Sequence (test_kuzu_readwrite_connectivity)
- **Capability**: `kuzu_4dtes_persistence`
- **Action Type**: `write_integration_test`
- **Priority**: HIGH
- **Can Execute Now**: `False`
- **Requires Human Approval**: `True`
- **Commands to Run**:
  - `.venv/bin/python layers/l2_brain/tests/test_four_dtes_persistence_preflight.py`

### Toggle Production Kùzu Persistent Database Adapter (enable_production_kuzu_adapter)
- **Capability**: `kuzu_4dtes_persistence`
- **Action Type**: `enable_adapter`
- **Priority**: MEDIUM
- **Can Execute Now**: `False`
- **Requires Human Approval**: `True`
- **Verification Commands**:
  - `dummie-ctl 4dtes-preflight`

### Configure Offline Sentence Transformers Embedding Adapter (configure_local_sentence_transformers)
- **Capability**: `real_semantic_embeddings`
- **Action Type**: `enable_adapter`
- **Priority**: MEDIUM
- **Can Execute Now**: `False`
- **Requires Human Approval**: `True`
- **Commands to Run**:
  - `.venv/bin/pip install sentence-transformers`
- **Verification Commands**:
  - `.venv/bin/python -c 'import sentence_transformers'`

### Execute All Dynamic Test Cases and Clean Up Orphans (run_regression_testing)
- **Capability**: `full_regression_suite`
- **Action Type**: `run_full_regression`
- **Priority**: HIGH
- **Can Execute Now**: `False`
- **Requires Human Approval**: `True`
- **Commands to Run**:
  - `pytest layers/l2_brain/tests/`

### Safely Archive and Prune Shadow/Duplicate Code Modules (archive_redundant_shadow_files)
- **Capability**: `shadow_module_resolution`
- **Action Type**: `repair_mapping`
- **Priority**: LOW
- **Can Execute Now**: `False`
- **Requires Human Approval**: `True`
- **Commands to Run**:
  - `mkdir -p .aiwg/archive`
  - `mv layers/l2_brain/shadow_*.py .aiwg/archive/ || true`

### Resolve Missing Physical Evidence Spec Audit Files (generate_spec_physical_evidence)
- **Capability**: `spec_runtime_mapping`
- **Action Type**: `write_integration_test`
- **Priority**: MEDIUM
- **Can Execute Now**: `False`
- **Requires Human Approval**: `True`
- **Commands to Run**:
  - `python3 scripts/validate_specs_docs.py`

