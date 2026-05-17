# Runtime Closure Plan Report
**Decision**: PASS_WITH_WARNINGS

## Actionable Repair Steps (Human Gated)
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

