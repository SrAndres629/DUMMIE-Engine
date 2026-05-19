# Active Pack Contract — PACK_3.2

* **Pack ID**: `PACK_3.2`
* **Title**: `CODE Embedding Provider`
* **Objective**: Separar el espacio vectorial de texto del espacio de código y sintaxis abstracta.

---

## Plan and Boundaries

### Short-Term Goal
Implementar el proveedor de embeddings de CODE para separar el espacio vectorial de texto.

### Why Now?
Para evitar la colisión semántica entre lenguaje natural y sintaxis de código.

### Out of Scope
* Iniciar Pack 3.3.

---

## Constraints & Requirements

### Files Expected to Change
* `layers/l2_brain/ast_indexer.py`

### Files Forbidden to Change
* `layers/l2_brain/embedding_mesh/reranker.py`
* `layers/l2_brain/embedding_mesh/contracts.py`

### Required Tests
* `layers/l2_brain/tests/test_structural_hardening_contracts.py`

---

## Risks & Fallbacks

* **Regression Risks**: Duplicación de caché vectorial en memoria.
* **Rollback Plan**: revertir cambios de Pack 3.2
* **Stop Conditions**: 
  - no iniciar si preflight falla
  - si TEXT_FAST se degrada
  - si CODE vector space mezcla con TEXT_FAST
