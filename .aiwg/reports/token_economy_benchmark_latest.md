# Token Economy Benchmark Report

**Decision:** PASS
**Reduction Ratio (Raw/Surgical):** 26121.43x
**Efficiency Score:** 100.0/100
**Measurement Type:** deterministic_estimate

## Strategy Comparison

| Strategy | Est. Tokens | Items | Evidence | Description |
| :--- | :--- | :--- | :--- | :--- |
| raw_folder_naive_estimate | 78364286 | 4515 | ✅ | Read everything in the workspace. |
| repo_inventory_only | 5000 | 1 | ❌ | Read only the git-tracked file list. |
| folder_dossier_context | 20000 | 2257 | ✅ | Read AST dossiers for relevant layers. |
| repo_intelligence_plus_selected_dossiers | 8000 | 10 | ✅ | Read manifest + targeted deep dossiers. |
| memory_spine_plus_selected_dossiers | 3000 | 5 | ✅ | Read causal memory + surgical deep dossiers. |
