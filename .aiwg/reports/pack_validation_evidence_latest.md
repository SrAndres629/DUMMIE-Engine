# Pack Validation Evidence (Automated Runner)
    
* **Result**: PASSED
* **Suite Name**: aiwg_evidence_runner
* **Commit**: d63cd3f2de88c870dbaedaaf4ceb4b6f80211ce4
* **Duration**: 11.25 seconds
* **Started At**: 2026-05-19T05:40:08.563958Z
* **Finished At**: 2026-05-19T05:40:19.818766Z
* **Command**: `PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_aiwg_pack_guard.py && python3 scripts/validate_specs_docs.py && PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_pack3_1_hybrid_reranker.py && PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_embedding_mesh_contracts.py && PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_embedding_mesh_router.py && PYTHONPATH=. layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/test_semantic_hardening_index.py`
* **Exit Code**: 0
* **Stdout Log**: `.aiwg/reports/validation_logs/PACK_3.2/stdout.log`
* **Stderr Log**: `.aiwg/reports/validation_logs/PACK_3.2/stderr.log`
* **Python Executable**: `/usr/bin/python3`
