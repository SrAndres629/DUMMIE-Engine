# Pack Validation Evidence (Automated Runner)
    
* **Result**: PASSED
* **Suite Name**: aiwg_evidence_runner
* **Commit**: ce6de196915f5ace8d9f58f1576703b31b2212f4
* **Duration**: 7.37 seconds
* **Started At**: 2026-05-19T04:55:50.644962Z
* **Finished At**: 2026-05-19T04:55:58.019913Z
* **Command**: `PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_aiwg_pack_guard.py && python3 scripts/validate_specs_docs.py && PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_pack3_1_hybrid_reranker.py && PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_embedding_mesh_contracts.py && PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_embedding_mesh_router.py && PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_semantic_hardening_index.py`
* **Exit Code**: 0
* **Stdout Log**: `.aiwg/reports/validation_logs/PACK_3.2/stdout.log`
* **Stderr Log**: `.aiwg/reports/validation_logs/PACK_3.2/stderr.log`
* **Python Executable**: `/usr/bin/python3`
