# Architectural Decision Log — DUMMIE Engine

This documents all architectural and governance decisions made during the execution of DUMMIE packs.

---

## 1. ADR-001: Strict Regression Gates on Report Status
* **Date**: `2026-05-19`
* **Context**: Pack 3.1 reports were compiled using wrong Python interpreter, leading to silent degradation.
* **Decision**: Separate degraded_embeddings count from reranker status, and enforce strict pytest regression checks of report files.
* **Alternatives Considered**: Manual report audit before each commit.
* **Consequences**: Stable and persistent validation of semantic layers across all branches.
* **Rollback**: Disable reports validation in test suite.
* **Related Pack**: `PACK_3.1`
* **Related Files**: `layers/l2_brain/tests/test_pack3_1_hybrid_reranker.py`
