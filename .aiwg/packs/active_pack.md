# Active Pack Contract — PACK_3.1_MERGE_GATE

* **Pack ID**: `PACK_3.1_MERGE_GATE`
* **Title**: `Hybrid+ Reranker Main Closure & AIWG Kernel Integration`
* **Objective**: Cerrar definitivamente el Pack 3.1 en main y asegurar el gobierno via el Execution Kernel de `.aiwg`.

---

## Plan and Boundaries

### Short-Term Goal
Integrar el Execution Kernel de gobierno vial `.aiwg` y consolidar tests de resiliencia.

### Why Now?
Es imperativo evitar la fragmentación de sub-parches de desarrollo en ramas paralelas y tener métricas acumulativas.

### Out of Scope
* Iniciar Pack 3.2.

---

## Constraints & Requirements

### Files Expected to Change
* `scripts/aiwg_pack_guard.py`
* `layers/l2_brain/tests/test_aiwg_pack_guard.py`

### Files Forbidden to Change
* `layers/l2_brain/embedding_mesh/reranker.py`
* `layers/l2_brain/embedding_mesh/contracts.py`

### Required Tests
* `layers/l2_brain/tests/test_aiwg_pack_guard.py`

---

## Risks & Fallbacks

* **Regression Risks**: Errores de sintaxis o import en los validadores del pack guard.
* **Rollback Plan**: Revertir cambios estructurales de los scripts de `.aiwg`.
* **Stop Conditions**: No iniciar Pack 3.2 hasta haber completado el merge de Pack 3.1 e implementar el guard de gobierno.
