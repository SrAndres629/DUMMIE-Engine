# Architecture Eradication & Sustainable Code Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Erradicar deuda estructural en L0/L1/L2, formalizar auditorías continuas y estandarizar prácticas de código sostenible sin borrado destructivo.

**Architecture:** Programa por fases con puertas de verificación. Primero se estabiliza compilación/contratos de ruta/import, luego se elimina acoplamiento cruzado de capas, después se endurece gobernanza `.aiwg`, y finalmente se instala una disciplina repo-wide con métricas y CI. Cada fase produce evidencia verificable.

**Tech Stack:** Python 3.11+, Go, Elixir, Bash, pytest, go test, ripgrep, Make, esquemas JSON/YAML.

---

## Scope & Version

- Programa: `AEP` (Architecture Eradication Program)
- Versión inicial: `v1.0.0`
- Horizonte:
- Corto plazo (0-2 semanas): recuperación de integridad operativa
- Mediano plazo (1-3 meses): convergencia arquitectónica por capas
- Largo plazo (3-12 meses): gobernanza sostenible automatizada

## File Map (Plan Artifacts)

- Plan principal (este documento): `docs/superpowers/plans/2026-05-19-architecture-eradication-sustainable-code.md`
- Roadmap operativo `.aiwg`: `.aiwg/roadmap/architecture_eradication_program_v1.md`
- Política repo-wide: `docs/ops/sustainable-code-program-v1.md`

## Chunk 1: Baseline y Reparación Crítica (Corto plazo)

### Task 1: Baseline de auditoría reproducible

**Files:**
- Create: `scripts/audit_import_boundaries.py`
- Create: `scripts/audit_hardcoded_paths.py`
- Create: `scripts/audit_runtime_artifacts.py`
- Modify: `Makefile`
- Create: `state/audits/README.md`

- [ ] **Step 1: Escribir tests de contrato de auditoría (fallo esperado)**

Create:
- `scripts/tests/test_audit_import_boundaries.py`
- `scripts/tests/test_audit_hardcoded_paths.py`
- `scripts/tests/test_audit_runtime_artifacts.py`

- [ ] **Step 2: Validar fallo inicial**

Run: `pytest -q scripts/tests/test_audit_import_boundaries.py scripts/tests/test_audit_hardcoded_paths.py scripts/tests/test_audit_runtime_artifacts.py`
Expected: FAIL por scripts inexistentes.

- [ ] **Step 3: Implementar scripts mínimos**

Implement reglas:
- Prohibir `L2 -> L1` imports directos.
- Reportar hardcoded absolutos (`/home/...`, rutas máquina-local).
- Medir porcentaje de artefactos (`.venv`, `_build`, `deps`, `__pycache__`, `.pytest_cache`, `node_modules`).

- [ ] **Step 4: Conectar gate en Makefile**

Add targets:
- `verify-architecture`
- `verify-sustainability`

- [ ] **Step 5: Verificar paso**

Run: `make verify-architecture`
Expected: PASS con reporte en `state/audits/`.

- [ ] **Step 6: Commit**

```bash
git add scripts/audit_import_boundaries.py scripts/audit_hardcoded_paths.py scripts/audit_runtime_artifacts.py scripts/tests/test_audit_import_boundaries.py scripts/tests/test_audit_hardcoded_paths.py scripts/tests/test_audit_runtime_artifacts.py Makefile state/audits/README.md
git commit -m "chore: add architecture and sustainability audit gates"
```

### Task 2: Recuperar integridad sintáctica mínima L1/L2

**Files:**
- Modify: `layers/l1_nervous/adapters/mcp/server.py`
- Modify: `layers/l1_nervous/tests/industrial/test_e2e_flow.py`
- Modify: `layers/l1_nervous/tests/industrial/test_swarm_race.py`
- Modify: `layers/l1_nervous/tests/test_observe_swarm_perf.py`
- Modify: `layers/l2_brain/tests/test_dummied_ctl.py`

- [ ] **Step 1: Escribir test que compile todos los .py first-party**

Create: `scripts/tests/test_python_compile_first_party.py`

- [ ] **Step 2: Validar fallo inicial**

Run: `pytest -q scripts/tests/test_python_compile_first_party.py`
Expected: FAIL listando archivos con `SyntaxError`.

- [ ] **Step 3: Aplicar correcciones mínimas no funcionales**

- Reparar definiciones corruptas en `server.py`.
- Eliminar secuencias `pass pass # print(...)` inválidas.
- Mover `from __future__ import annotations` al inicio real del archivo.

- [ ] **Step 4: Verificar compilación**

Run: `pytest -q scripts/tests/test_python_compile_first_party.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add layers/l1_nervous/adapters/mcp/server.py layers/l1_nervous/tests/industrial/test_e2e_flow.py layers/l1_nervous/tests/industrial/test_swarm_race.py layers/l1_nervous/tests/test_observe_swarm_perf.py layers/l2_brain/tests/test_dummied_ctl.py scripts/tests/test_python_compile_first_party.py
git commit -m "fix: restore python syntax integrity in l1 and l2 test surfaces"
```

### Task 3: Contrato único de rutas persistentes L0/L1/L2

**Files:**
- Create: `layers/l0_overseer/internal/orchestrator/runtime_paths.go`
- Modify: `layers/l0_overseer/cmd/overseer/main.go`
- Modify: `layers/l0_overseer/internal/orchestrator/store.go`
- Modify: `layers/l1_nervous/adapters/mcp/server.py`
- Modify: `layers/l2_brain/whole_body_scanner.py`
- Modify: `layers/l2_brain/wiring_matrix_builder.py`
- Modify: `layers/l2_brain/shadow_runtime_classifier.py`
- Test: `layers/l2_brain/tests/infrastructure/test_kuzu_path_hardening.py`

- [ ] **Step 1: Escribir tests de path policy cross-layer**

Create: `scripts/tests/test_runtime_path_policy.py`

- [ ] **Step 2: Validar fallo inicial**

Run: `pytest -q scripts/tests/test_runtime_path_policy.py`
Expected: FAIL detectando hardcoded absolutos.

- [ ] **Step 3: Implementar path resolver por capa**

Regla canónica:
- Root desde `DUMMIE_ROOT`/`DUMMIE_ROOT_DIR` con fallback relativo al repo.
- Memoria Kùzu default en `.aiwg/memory/loci.db`.

- [ ] **Step 4: Verificar**

Run:
- `pytest -q scripts/tests/test_runtime_path_policy.py`
- `go test ./layers/l0_overseer/...`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add layers/l0_overseer/internal/orchestrator/runtime_paths.go layers/l0_overseer/cmd/overseer/main.go layers/l0_overseer/internal/orchestrator/store.go layers/l1_nervous/adapters/mcp/server.py layers/l2_brain/whole_body_scanner.py layers/l2_brain/wiring_matrix_builder.py layers/l2_brain/shadow_runtime_classifier.py scripts/tests/test_runtime_path_policy.py
git commit -m "refactor: standardize runtime path policy across l0 l1 l2"
```

## Chunk 2: Convergencia Arquitectónica por Capas (Mediano plazo)

### Task 4: Eliminar inversión de dependencia L2->L1

**Files:**
- Modify: `layers/l2_brain/daemon.py`
- Create: `layers/l2_brain/repo_guard.py` or `layers/l2_brain/domain/repo_guard.py`
- Modify: `layers/l1_nervous/repo_guard.py` (wrapper o deprecación controlada)
- Create: `layers/l2_brain/tests/test_layer_boundaries.py`

- [ ] **Step 1: Test de frontera de capas**

Rule:
- L2 no puede importar L1.

- [ ] **Step 2: Validar fallo inicial**

Run: `pytest -q layers/l2_brain/tests/test_layer_boundaries.py`
Expected: FAIL por import en `daemon.py`.

- [ ] **Step 3: Mover responsabilidad y ajustar imports**

- [ ] **Step 4: Verificar**

Run:
- `pytest -q layers/l2_brain/tests/test_layer_boundaries.py`
- `pytest -q layers/l2_brain/tests/test_daemon_hierarchical_planner.py`

- [ ] **Step 5: Commit**

```bash
git add layers/l2_brain/daemon.py layers/l2_brain/repo_guard.py layers/l1_nervous/repo_guard.py layers/l2_brain/tests/test_layer_boundaries.py
git commit -m "refactor: remove l2 to l1 dependency inversion"
```

### Task 5: Plan de migración de imports legacy a `src/brain`

**Files:**
- Create: `layers/l2_brain/import_migration_map.yaml`
- Modify: `layers/l1_nervous/bootstrap.py`
- Modify: `layers/l1_nervous/mcp_server.py`
- Modify: `layers/l2_brain/__init__.py`
- Create: `layers/l2_brain/tests/test_import_contracts.py`

- [ ] **Step 1: Definir mapa de equivalencias de módulos**

- [ ] **Step 2: Añadir test de no-regresión de imports**

Run: `pytest -q layers/l2_brain/tests/test_import_contracts.py`
Expected: FAIL inicial con huellas legacy no permitidas.

- [ ] **Step 3: Implementar wrappers de compatibilidad temporal**

- [ ] **Step 4: Verificar gates**

Run:
- `pytest -q layers/l2_brain/tests/test_import_contracts.py`
- `make verify-architecture`

- [ ] **Step 5: Commit**

```bash
git add layers/l2_brain/import_migration_map.yaml layers/l1_nervous/bootstrap.py layers/l1_nervous/mcp_server.py layers/l2_brain/__init__.py layers/l2_brain/tests/test_import_contracts.py
git commit -m "chore: add controlled import migration path for l2"
```

### Task 6: Limpieza no destructiva de artefactos por política

**Files:**
- Create: `scripts/quarantine_artifacts.sh`
- Create: `scripts/tests/test_quarantine_artifacts.py`
- Create: `state/trash/README.md`
- Modify: `.gitignore` (solo si faltan patrones)

- [ ] **Step 1: Test de cuarentena no destructiva**

- [ ] **Step 2: Validar fallo**

Run: `pytest -q scripts/tests/test_quarantine_artifacts.py`
Expected: FAIL por script inexistente.

- [ ] **Step 3: Implementar script de movimiento con manifest**

Output:
- `trash/YYYY-MM-DD/...`
- `trash/YYYY-MM-DD/manifest.csv`

- [ ] **Step 4: Verificar**

Run: `pytest -q scripts/tests/test_quarantine_artifacts.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/quarantine_artifacts.sh scripts/tests/test_quarantine_artifacts.py state/trash/README.md .gitignore
git commit -m "chore: add non-destructive artifact quarantine workflow"
```

## Chunk 3: Gobernanza `.aiwg` y Disciplina Repo-Wide (Largo plazo)

### Task 7: Contratos de auditoría en `.aiwg`

**Files:**
- Create: `.aiwg/control/governance/repo_audit_contract_v1.yaml`
- Create: `.aiwg/control/governance/sustainable_code_kpis_v1.yaml`
- Create: `.aiwg/schemas/repo_audit_report.schema.json`
- Modify: `.aiwg/roadmap/long_term_objectives.md`

- [ ] **Step 1: Definir contrato de auditoría y KPIs**

KPIs mínimos:
- Imports prohibidos por frontera
- Paths absolutos críticos
- Tasa de archivos sin tests asociados
- Porcentaje de artefactos runtime en capas core

- [ ] **Step 2: Añadir validación de esquema**

Create: `scripts/tests/test_repo_audit_schema.py`

- [ ] **Step 3: Verificar**

Run: `pytest -q scripts/tests/test_repo_audit_schema.py`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add .aiwg/control/governance/repo_audit_contract_v1.yaml .aiwg/control/governance/sustainable_code_kpis_v1.yaml .aiwg/schemas/repo_audit_report.schema.json .aiwg/roadmap/long_term_objectives.md scripts/tests/test_repo_audit_schema.py
git commit -m "governance: add aiwg repo audit contract and sustainability kpis"
```

### Task 8: Programa repo-wide de código sostenible

**Files:**
- Create: `docs/ops/sustainable-code-program-v1.md`
- Create: `.github/pull_request_template.md`
- Create: `.github/workflows/architecture-gates.yml`
- Modify: `AGENTS.md`

- [ ] **Step 1: Definir Definition of Done sostenible**

Requerir:
- test nuevo o actualizado por bugfix
- evidencia de verificación
- diff acotado
- no hardcoded absolutos nuevos

- [ ] **Step 2: Plantilla PR + gates automatizados**

- [ ] **Step 3: Verificar pipeline local**

Run: `make verify-specs && make verify-architecture && make verify-industrial`
Expected: PASS (o FAIL con reporte accionable).

- [ ] **Step 4: Commit**

```bash
git add docs/ops/sustainable-code-program-v1.md .github/pull_request_template.md .github/workflows/architecture-gates.yml AGENTS.md
git commit -m "docs: establish repo-wide sustainable code program and gates"
```

### Task 9: Ciclo de mentoría estratégica operacionalizada

**Files:**
- Create: `.aiwg/roadmap/quarterly_objective_cycles_v1.md`
- Create: `.aiwg/roadmap/checkpoints_short_medium_long_v1.yaml`
- Create: `scripts/goal_checkpoint_report.py`

- [ ] **Step 1: Definir cadencia de objetivos**

- Corto plazo: checkpoint operativo semanal
- Mediano plazo: consolidación mensual
- Largo plazo: revisión filosófica trimestral y evolución de objetivo

- [ ] **Step 2: Generar reporte automático de progreso**

Run: `python3 scripts/goal_checkpoint_report.py`
Expected: emite reporte markdown en `.aiwg/reports/goal_checkpoint_latest.md`.

- [ ] **Step 3: Commit**

```bash
git add .aiwg/roadmap/quarterly_objective_cycles_v1.md .aiwg/roadmap/checkpoints_short_medium_long_v1.yaml scripts/goal_checkpoint_report.py
git commit -m "feat: add strategic checkpoint cycle for short medium long objectives"
```

## Global Verification Gate (Before closing program)

Run:

```bash
git status --short
make verify-specs
make verify-architecture
make verify-industrial
rg -n "kuzu_data|MemoryState|m\.\*|rm -f.*kuzu|os\.remove\(" layers scripts doc -S
```

Expected:
- Sin errores críticos de compilación first-party.
- Sin hardcoded paths absolutos en rutas runtime críticas.
- Sin dependencia L2->L1.
- Reportes de auditoría disponibles en `state/audits/` y `.aiwg/reports/`.

## Delivery Strategy

- Estrategia de commits: 1 tarea = 1 commit.
- Cambios destructivos: prohibidos en este programa.
- Migraciones de estructura: siempre con wrappers temporales y pruebas de no-regresión.

## Risks & Mitigations

- Riesgo: romper imports legacy en L1/L2.
- Mitigación: wrappers de compatibilidad + `test_import_contracts.py`.

- Riesgo: ruido de auditoría por artefactos de ejecución.
- Mitigación: cuarentena no destructiva + manifests trazables.

- Riesgo: regresión silenciosa en paths persistentes.
- Mitigación: test de policy cross-layer + auditoría hardcoded en CI.

## Completion Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-19-architecture-eradication-sustainable-code.md`. Ready to execute?
