# Active Pack Contract - PACK_S1 ACTIVE

* **Pack ID**: `PACK_S1`
* **Title**: `Sovereign CLI + SDK + Strategic Partner Runtime`
* **Objective**: Mantener el runtime soberano, la CLI/SDK y la coordinacion del swarm alineados con la verdad fisica verificada.
* **Status**: `ACTIVE`

---

## Runtime Truth

* **Current Pack**: `PACK_S1`
* **Last Completed Pack**: `INMEDIATO`
* **Next Swarm Pack**: `PACK_10`
* **Swarm Backlog**: `13/14 completed`, `1 pending`

---

## PACK_10 Coordination

* Evidence directory: `.aiwg/agent_mesh/debate/evidence/PACK_10/`
* Regression test: `layers/l2_brain/tests/test_aiwg_runtime_truth_coherence.py`
* Guardrail: do not use stale `PACK_4.1` or missing `daemon_service.py` as current runtime truth.

---

## Verification Commands

* `PYTHONDONTWRITEBYTECODE=1 uv run pytest -q layers/l2_brain/tests/test_aiwg_runtime_truth_coherence.py`
* `PYTHONDONTWRITEBYTECODE=1 uv run pytest -q layers/l2_brain/tests/test_aiwg_pack_guard.py`
* `PYTHONDONTWRITEBYTECODE=1 uv run python -c "import dummie.engine; import layers.l2_brain; print('IMPORT_OK')"`
* `./scripts/dummie status`

---

# Reorientation Rule

If another agent follows a stale state plane, stop it, point it to `current_truth.json`, `active_pack.json`, the swarm backlog, and physical verification output, then require one small verified next step.
