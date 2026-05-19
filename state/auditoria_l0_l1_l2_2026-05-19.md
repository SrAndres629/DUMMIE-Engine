# Auditoría Arquitectónica L0/L1/L2 (2026-05-19)

## Alcance
- `layers/l0_overseer`
- `layers/l1_nervous`
- `layers/l2_brain`

## Métricas Base
- Tamaño bruto:
  - L0: 34M
  - L1: 672M
  - L2: 5.5G
- Archivos por capa (visible via `rg --files`):
  - L0: 30
  - L1: 106
  - L2: 487
- Top-level files:
  - L0: 8
  - L1: 30
  - L2: 173

## Descomposición de tamaño útil vs artefactos
- L0 total=32,420,201; artefactos=18,968,266; útil=13,451,935
- L1 total=671,200,871; artefactos=474,291,581; útil=196,909,290
- L2 total=5,708,190,401; artefactos=5,705,017,011; útil=3,173,390
- Observación crítica: en L2, `.venv` representa ~99.94% del tamaño.

## Hallazgos Críticos
1. Archivo de servidor MCP inválido sintácticamente en L1.
   - Evidencia: `layers/l1_nervous/adapters/mcp/server.py:4`
   - Error: `SyntaxError: expected '('`
2. Tests con sintaxis rota en L1 y L2.
   - Evidencia:
     - `layers/l1_nervous/tests/industrial/test_e2e_flow.py:12`
     - `layers/l1_nervous/tests/industrial/test_swarm_race.py:24`
     - `layers/l1_nervous/tests/test_observe_swarm_perf.py:64`
     - `layers/l2_brain/tests/test_dummied_ctl.py:2`
3. Paths absolutos hardcodeados en runtime (rompe portabilidad).
   - Evidencia:
     - `layers/l0_overseer/cmd/overseer/main.go:15`
     - `layers/l0_overseer/internal/orchestrator/store.go:24`
     - `layers/l1_nervous/adapters/mcp/server.py:34`
     - `layers/l2_brain/whole_body_scanner.py:38`
     - `layers/l2_brain/wiring_matrix_builder.py:16`
     - `layers/l2_brain/shadow_runtime_classifier.py:16`
4. Inversión de dependencia entre capas (L2 depende de L1).
   - Evidencia: `layers/l2_brain/daemon.py:67`

## Hallazgos Altos
1. Acoplamiento por namespace mixto y deuda de empaquetado.
   - L1->L2 imports: 21
   - L1->brain imports: 9
   - L2 flat self-imports (`layers.l2_brain.*`): 414
   - L2 `brain.*` imports en `src`: 64
2. Uso extendido de `sys.path` hacks (runtime frágil).
   - Evidencia: múltiples ocurrencias en L1/L2/scripts (bootstrap, mcp_server, tests, CLI).
3. L0 versiona dependencias y build outputs.
   - Evidencia (`git ls-files`):
     - `layers/l0_overseer/deps`: 596 archivos trackeados
     - `layers/l0_overseer/_build`: 402 archivos trackeados
4. Manejo de errores silencioso.
   - Evidencia:
     - `layers/l2_brain/socraticode_gateway_adapter.py:90,97`
     - `layers/l1_nervous/mcp_proxy.py:116`

## Hallazgos Medios
1. Sprawl de módulos en raíz de L2 (173 archivos top-level; 167 `.py`).
2. Convivencia de dos arquitecturas en L2:
   - Flat legacy: `layers/l2_brain/*.py`
   - Hexagonal parcial: `layers/l2_brain/src/brain/*`
3. Operaciones potencialmente destructivas sobre DB/locks sin estrategia transaccional explícita.
   - Evidencia: `layers/l2_brain/infrastructure/adapters/kuzu.py:35,49`

## Señales Positivas
1. Cobertura de pruebas amplia en L2 (211 archivos de test detectados).
2. Intento explícito de estandarizar ruta Kùzu hacia `.aiwg/memory/loci.db` en múltiples componentes.
3. README de L2 reconoce deuda y gaps de contrato (`layers/l2_brain/README.md`).

## Diagnóstico por capa
- L0 (`l0_overseer`): base funcional, pero contaminada por artefactos/deps versionadas y hardcoded paths.
- L1 (`l1_nervous`): capa de integración poderosa pero frágil por hacks de import y archivos con sintaxis rota.
- L2 (`l2_brain`): núcleo más avanzado, pero en transición incompleta entre arquitectura plana y `src/brain`.

## Priorización de reparación (sin borrar nada)
1. Restaurar compilabilidad mínima (archivos Python rotos críticos).
2. Eliminar hardcoded absolutos usando una sola política de rutas.
3. Romper dependencia L2->L1 moviendo `RepoGuard` a contrato neutral (o L2-domain).
4. Congelar el layout objetivo (`src/brain`) y migrar por vertical slices con wrappers de compatibilidad.
5. Aislar artefactos runtime (`.venv`, `_build`, `deps`) fuera del core lógico operativo del repo.

## Estado de ejecución de auditoría
- No se borró ni movió ningún archivo.
- No se ejecutó suite completa de tests (auditoría estructural y sintáctica únicamente).

