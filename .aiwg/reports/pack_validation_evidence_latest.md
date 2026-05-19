# Pack Validation Evidence (Automated Runner)
    
* **Result**: PASSED
* **Suite Name**: aiwg_evidence_runner
* **Commit**: 7b5867026bc48cdf37bce675d08fc8966bca3056
* **Duration**: 10.07 seconds
* **Started At**: 2026-05-19T04:51:05.709346Z
* **Finished At**: 2026-05-19T04:51:15.784565Z
* **Command**: `PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_aiwg_pack_guard.py && python3 scripts/validate_specs_docs.py && PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_pack3_1_hybrid_reranker.py && PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_embedding_mesh_contracts.py && PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_embedding_mesh_router.py && PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_semantic_hardening_index.py`
* **Exit Code**: 0
* **Stdout Log**: `.aiwg/reports/validation_logs/PACK_3.2/stdout.log`
* **Stderr Log**: `.aiwg/reports/validation_logs/PACK_3.2/stderr.log`
* **Python Executable**: `/usr/bin/python3`
