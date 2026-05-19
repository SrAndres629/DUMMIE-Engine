# DUMMIE Engine Roadmap Ledger — Path to Pack 6.1

This ledger is a live, verifiable, and contract-governed roadmap from the current reconciled baseline to the Minimal Golden Path (Pack 6.1).

---

## 🗺️ Reconciled Rehearsal Status (CURRENT_TRUTH)

- **HEAD Commit**: `06478a1fa387c7bdbaab6b87ffc20d7ecb2e7702` (origin/main parity achieved)
- **Active Structural State**:
  - `pack_status`: `PASS_WITH_WARNINGS`
  - `repo_health_status`: `FAIL` (due to active high-risk legacy and unclassified debt)
  - `CRITICAL`: `0`
  - `HIGH`: `44`
  - `SHADOW_CANDIDATE`: `44`
  - `ORPHAN_TEST_CANDIDATE`: `3`
  - `bound_active_runtime`: `31`
  - `deferred_no_safe_action`: `0`
  - `toolchain_validated`: `5`
  - `toolchain_missing`: `0`
- **Reconciled Packs in Main**:
  - **Pack 2.2** (Polyglot Toolchain Binding): Verified at `f0345c8`
  - **Pack 2.3** (L2 High Batch Binding): Verified at `c1f7de4`
  - **Pack 2.3 Shellcheck/Polyglot Batch**: Verified at `06478a1`
- **Next Active Phase**: **Pack 2.4 — Superficial Tests Upgrade** (Active Execution)

---

## 📦 Core Hardening Roadmap Definition (Packs 2.2 to 6.1)

---

### **PACK 2.2-G — Merge Gate Polyglot Toolchain**
*Status*: **COMPLETED**
- **Objetivo**: Llevar el endurecimiento políglota de la herramienta L1 a `main`.
- **Precondiciones**: Rama `hardening/structural-pack-2.2-polyglot-binding` pasa test local.
- **Archivos Probables**: `layers/l1_nervous/sidecar.go`, `layers/l1_nervous/ssh_sandbox_wrapper.sh`.
- **Comandos**: `git merge --no-ff`
- **Tests**: `pytest` del clasificador de triage.
- **Métricas Antes/Después**:
  - `deferred_no_safe_action`: `7` ➡️ `0`
  - `HIGH`: `71` ➡️ `64`
- **Riesgos**: Mínimo.
- **Done Criteria**: origin/main contiene commit `f0345c8`.
- **Blast Radius**: Nulo (L1 toolchain validation only).
- **Rollback**: `git checkout checkpoint/structural-hardening-pack-2.2`.
- **Plan**: Completado y consolidado.

---

### **PACK 2.3 — L2 High Batch Binding**
*Status*: **COMPLETED**
- **Objetivo**: Enlazar de forma segura 20 candidatos shadow de alta prioridad L2.
- **Precondiciones**: Pack 2.2-G cerrado.
- **Archivos Probables**: `layers/l2_brain/structural_hardening/bindings.py`.
- **Comandos**: `python3 scripts/build_structural_hardening_triage.py --repo-root . --write-reports`
- **Tests**: `layers/l2_brain/tests/test_pack2_3_l2_bindings_smoke.py`.
- **Métricas Antes/Después**:
  - `SHADOW_CANDIDATE`: `64` ➡️ `44`
  - `bound_active_runtime`: `11` ➡️ `31`
- **Riesgos**: Ruido de imports en Python.
- **Done Criteria**: 8 smoke tests pasando; triage reflejando la caída exacta de candidatos.
- **Blast Radius**: Bajo (Metadata-only binding).
- **Rollback**: `git revert c1f7de4`.
- **Plan**: Completado y consolidado en `main`.

---

### **PACK 2.4 — Superficial Tests Upgrade**
*Status*: **ACTIVE EXECUTION**
- **Objetivo**: Convertir tests import-only/assert-free en pruebas de comportamiento reales con invariantes.
- **Precondiciones**: Paridad con `main` y pruebas unitarias de triage estables.
- **Archivos Probables**: 
  - `layers/l2_brain/tests/test_six_dimensional_context_runtime.py`
  - `layers/l2_brain/tests/test_daemon_gateway_heartbeat_bridge.py`
  - `layers/l2_brain/tests/test_embedding_memory_router.py`
  - `layers/l2_brain/tests/test_polyglot_probe_orchestrator.py`
  - `layers/l2_brain/tests/test_context_packet_optimizer.py`
  - `layers/l2_brain/tests/test_cognitive_bias_detector.py`
- **Comandos**: `layers/l2_brain/.venv/bin/pytest -v layers/l2_brain/tests/...`
- **Tests**: Pruebas reescritas con aserciones rigurosas de comportamiento.
- **Métricas Antes/Después**:
  - `superficial_tests` (heuristic): `13` ➡️ `< 7`
- **Riesgos**: Falsos positivos si el comportamiento del mock diverge del runtime real.
- **Done Criteria**: Tests modificados ejecutan con múltiples aserciones explícitas y lógica de invariantes contractuales.
- **Blast Radius**: Medio-Bajo (Afecta únicamente suite de pruebas L2).
- **Rollback**: `git checkout -- layers/l2_brain/tests/`
- **Plan**: Ejecutar ahora.

---

### **PACK 2.5 — UNKNOWN Classification Batch**
*Status*: **DEFERRED** (Siguiente fase de limpieza de metadatos)
- **Objetivo**: Clasificar lote masivo de archivos en estado `UNKNOWN` según métricas de fan-in e importancia.
- **Precondiciones**: Pack 2.4 cerrado y pruebas de comportamiento integradas.
- **Archivos Probables**: 144 archivos `UNKNOWN` en L0, L1 y L2.
- **Comandos**: `python3 scripts/build_structural_hardening_triage.py --write-reports`
- **Tests**: `test_structural_hardening_classifier.py`
- **Métricas Antes/Después**:
  - `UNKNOWN`: `144` ➡️ `< 80`
- **Riesgos**: Clasificación incorrecta como `LEGACY` sin evidencia real.
- **Done Criteria**: Menos de 80 archivos `UNKNOWN` remanentes.
- **Blast Radius**: Bajo (Metadata registry).
- **Rollback**: Revertir cambios en `layers/l2_brain/structural_hardening/bindings.py`.
- **Plan**: Ejecutar después de consolidar Pack 2.4.

---

### **PACK 2.6 — Orphan Tests + Frozen Scripts**
*Status*: **DEFERRED**
- **Objetivo**: Validar los 3 `ORPHAN_TEST_CANDIDATE` y congelar formalmente los scripts en desuso.
- **Precondiciones**: Registros L0/L1 actualizados en Pack 2.5.
- **Archivos Probables**: `layers/l2_brain/structural_hardening/bindings.py`.
- **Comandos**: `python3 scripts/build_structural_hardening_triage.py --write-reports`
- **Tests**: `test_structural_hardening_triage.py`
- **Métricas Antes/Después**:
  - `ORPHAN_TEST_CANDIDATE`: `3` ➡️ `0`
- **Riesgos**: Asignación incorrecta de pertenencia de módulos.
- **Done Criteria**: `ORPHAN_TEST_CANDIDATE = 0`.
- **Blast Radius**: Nulo.
- **Rollback**: Revertir cambios en bindings.
- **Plan**: Ejecutar secuencialmente.

---

### **PACK 2.7 — CI + Freshness Gates**
*Status*: **DEFERRED**
- **Objetivo**: Bloquear la integración si los reportes de triage y specs no están actualizados al HEAD del commit.
- **Precondiciones**: Ejecución local exitosa de todos los validadores.
- **Archivos Probables**: `.github/workflows/ci.yml` (o script local de Git Hooks).
- **Comandos**: `python3 scripts/validate_specs_docs.py`
- **Tests**: CI pre-commit checks.
- **Métricas Antes/Después**: Evita desalineación de commits en reportes de triage (`stale_report_fail`).
- **Riesgos**: Bloqueo accidental de flujos rápidos de desarrollo.
- **Done Criteria**: CI falla automáticamente si un reporte no coincide con HEAD del commit actual.
- **Blast Radius**: Medio (Modifica políticas de commits del repositorio).
- **Rollback**: Desactivar Hooks de Git.
- **Plan**: Ejecutar antes del salto funcional a la capa vectorial (Pack 3.0).

---

### **PACK 2.8 — Repo Health Recalibration**
*Status*: **DEFERRED**
- **Objetivo**: Transición formal del estado del repositorio a PASS con advertencias legítimas.
- **Precondiciones**: Cumplir todos los umbrales de deuda estructural.
- **Archivos Probables**: `layers/l2_brain/structural_hardening/classifier.py`.
- **Comandos**: `python3 scripts/build_structural_hardening_triage.py`
- **Tests**: `test_structural_hardening_classifier.py`
- **Métricas Antes/Después**:
  - `repo_health_status`: `FAIL` ➡️ `PASS_WITH_WARNINGS`
- **Riesgos**: Relajar excesivamente las barreras del linter del triage.
- **Done Criteria**: `CRITICAL = 0`, `HIGH < 20`, `SHADOW < 20`, `UNKNOWN < 30`.
- **Blast Radius**: Bajo (Metadata display change).
- **Rollback**: Revertir límites en `classifier.py`.
- **Plan**: Ejecutar como el cierre absoluto de la deuda L2/L1 de metadatos.

---

### **PACK 3.0 — Real TEXT_FAST Embedding Provider**
*Status*: **DEFERRED**
- **Objetivo**: Integrar un proveedor de embeddings local/rápido de forma nativa sin depender exclusivamente de `fallback_hash_384`.
- **Precondiciones**: Hardening estructural consolidado en `PASS_WITH_WARNINGS`.
- **Archivos Probables**: `layers/l2_brain/embedding_provider.py`.
- **Comandos**: `pytest layers/l2_brain/tests/test_embedding_mesh_contracts.py`
- **Tests**: Pruebas de regresión del vector space.
- **Métricas Antes/Después**:
  - `embedding_provider_mode`: `fallback_only` ➡️ `vector_space_active`
- **Riesgos**: Descarga inesperada de binarios o modelos gigantes en tiempo de ejecución.
- **Done Criteria**: Modelo local ligero cargado correctamente con fallback seguro en hash-384 ante fallos de persistencia.
- **Blast Radius**: Alto (Afecta el rendimiento de retrieval semántico).
- **Rollback**: Configuración por variable de entorno para desactivar proveedor nativo.
- **Plan**: Iniciar Bloque B.

---

### **PACK 3.1 — Reranker Real or Hybrid+**
*Status*: **DEFERRED**
- **Objetivo**: Integrar lógica de reordenamiento híbrido para los resultados de KùzuDB/Embeddings.
- **Precondiciones**: Pack 3.0 operativo.
- **Archivos Probables**: `layers/l2_brain/domain/retrieval_service.py`.
- **Tests**: `test_vault_embedding_index.py`
- **Métricas Antes/Después**: Aumento en precisión semántica (Recall@K).
- **Riesgos**: Latencia de inferencia local.
- **Done Criteria**: Los resultados de búsqueda se ponderan híbrida e incrementalmente con pesos de recencia e importancia.
- **Blast Radius**: Medio-Alto.
- **Rollback**: Bypass del paso de reranking en el pipeline de consulta.
- **Plan**: Posterior a Pack 3.0.

---

### **PACK 3.2 — CODE Embedding Provider**
*Status*: **DEFERRED**
- **Objetivo**: Separar el espacio vectorial de texto del espacio de código y sintaxis abstracta.
- **Precondiciones**: Servidor MCP local e indexador AST robusto.
- **Archivos Probables**: `layers/l2_brain/ast_indexer.py`.
- **Tests**: `test_structural_hardening_contracts.py`
- **Métricas Antes/Después**: Aislamiento de namespaces de búsqueda (código vs especificaciones).
- **Riesgos**: Duplicación de caché vectorial en memoria.
- **Done Criteria**: Consultas sintácticas devuelven resultados del parser sintáctico AST y no del corpus textual genérico.
- **Blast Radius**: Medio.
- **Rollback**: Unificar namespaces en la configuración de la base de datos de loci.
- **Plan**: Iniciar de forma diferida.

---

### **PACK 3.3 — Direct Spec Linkage Engine**
*Status*: **DEFERRED**
- **Objetivo**: Aumentar la precisión del linkage entre código y contratos Markdown (`direct_spec_hit_rate`).
- **Precondiciones**: Pack 3.2 terminado.
- **Archivos Probables**: `scripts/validate_specs_docs.py`.
- **Tests**: `test_structural_hardening_classifier.py`
- **Métricas Antes/Después**:
  - `direct_spec_hit_rate`: `< 50%` ➡️ `> 90%`
- **Riesgos**: Rigidez contractual insostenible durante desarrollo rápido.
- **Done Criteria**: Todo módulo con status `BOUND_ACTIVE_RUNTIME` cuenta con especificación directa explícita en su declaración.
- **Blast Radius**: Bajo.
- **Rollback**: Permitir fallback a enlaces de scope amplios.
- **Plan**: Ejecutar para consolidar Bloque B.

---

### **PACK 4.0 — ModelCapability Registry**
*Status*: **DEFERRED**
- **Objetivo**: Formalizar el contrato contractual e interfaces de los modelos especialistas (code, reasoning, etc.).
- **Precondiciones**: Bloque B finalizado de forma estable.
- **Archivos Probables**: `layers/l2_brain/domain/dtos.py`, `layers/l2_brain/gateway_contract.py`.
- **Tests**: `test_sdd_advanced_capabilities.py`
- **Done Criteria**: Interfaz JSON Schema unificada para registrar capacidades de LLMs sin requerir implementaciones físicas masivas.
- **Blast Radius**: Medio.
- **Rollback**: Uso del fallback de API directo.
- **Plan**: Iniciar Bloque C.

---

### **PACK 4.1 — ModelRouter v2**
*Status*: **DEFERRED**
- **Objetivo**: Enrutar dinámicamente tareas a modelos especialistas basándose en complejidad, tokens, costo, presupuesto e intención.
- **Precondiciones**: Pack 4.0 operativo.
- **Archivos Probables**: `layers/l2_brain/domain/reasoning_logic.py`, `layers/l2_brain/domain/dtos.py`.
- **Tests**: `test_model_router.py`
- **Done Criteria**: Solicitudes complejas son asignadas secuencialmente a través de un grafo de enrutamiento basado en costo histórico.
- **Blast Radius**: Alto.
- **Rollback**: Forzar enrutamiento a modelo generalista por defecto.
- **Plan**: Diferido.

---

### **PACK 4.2 — Guardrail Layer**
*Status*: **DEFERRED**
- **Objetivo**: Asegurar el escaneo de seguridad PII, secretos y comandos destructivos antes de interactuar con herramientas externas.
- **Precondiciones**: Registry 4.0 estructurado.
- **Archivos Probables**: `layers/l3_shield/formal_bridge.py`.
- **Tests**: `test_shield_bypass_blocked.py`
- **Done Criteria**: Bloqueo absoluto de inyecciones de comandos en tiempo de ejecución.
- **Blast Radius**: Alto (Seguridad perimetral activa).
- **Rollback**: Desactivación vía switch de depuración.
- **Plan**: Iniciar Bloque C.

---

### **PACK 4.3 — Function Calling Contract Layer**
*Status*: **DEFERRED**
- **Objetivo**: Estandarizar respuestas e invocación de herramientas externas basadas en esquemas JSON válidos con taxonomías de error precisas.
- **Precondiciones**: Pack 4.2 integrado.
- **Archivos Probables**: `layers/l1_nervous/mcp_registry.py`.
- **Tests**: `test_metagateway_operational.py`
- **Done Criteria**: Invocaciones mal formadas fallan explícitamente en el límite de la capa L1 antes de propagarse.
- **Blast Radius**: Medio-Alto.
- **Rollback**: Retornar a invocaciones directas dinámicas sin validación estricta de esquema.
- **Plan**: Iniciar Bloque C.

---

### **PACK 4.4 — Code LLM Integration**
*Status*: **DEFERRED**
- **Objetivo**: Incorporar el asistente de programación autónomo local/remoto integrado en el workbench y aislado bajo una sandbox de pruebas local.
- **Precondiciones**: Aislamiento de llamadas a herramientas garantizado.
- **Archivos Probables**: `layers/l2_brain/cognition/pattern_miner_v2.py`.
- **Tests**: `test_self_programming.py`
- **Done Criteria**: Los parches de código se evalúan y compilan en un subproceso sandbox seguro antes de aplicarse físicamente al espacio de trabajo.
- **Blast Radius**: Muy Alto (Modificación de código autónomo).
- **Rollback**: Bloqueo manual de commits automatizados.
- **Plan**: Cierre de Bloque C.

---

### **PACK 5.0 — Document Intelligence / LangExtract Adapter**
*Status*: **DEFERRED**
- **Objetivo**: Integrar el parser estructurado para lectura y extracción grounded de especificaciones técnicas y documentación de gran tamaño.
- **Precondiciones**: Entrada de Bloque D.
- **Archivos Probables**: `layers/l2_brain/domain/retrieval_service.py`.
- **Tests**: `test_vault_curator.py`
- **Done Criteria**: Extracción exitosa con trazabilidad (Spans exactos) desde fuentes Markdown/PDF.
- **Blast Radius**: Medio.
- **Rollback**: Caída a búsquedas semánticas tradicionales.
- **Plan**: Iniciar Bloque D.

---

### **PACK 5.1 — Runtime Context Compression Policy**
*Status*: **DEFERRED**
- **Objetivo**: Reducir el tamaño de las inyecciones de contexto mediante compresión adaptativa del historial y buffer de tokens.
- **Precondiciones**: Pack 5.0 completado.
- **Archivos Probables**: `layers/l2_brain/context_circulation_runtime.py`.
- **Tests**: `test_context_quant_runtime.py`
- **Done Criteria**: Compresión exitosa de un 40% de tokens inútiles garantizando retención de entidades fundamentales.
- **Blast Radius**: Medio.
- **Rollback**: Desactivar compresión (Contexto completo).
- **Plan**: Iniciar incrementalmente.

---

### **PACK 5.2 — Local Inference Backend Registry**
*Status*: **DEFERRED**
- **Objetivo**: Inventariar dinámicamente y orquestar inferencias locales utilizando Ollama, MLX o llama.cpp si están disponibles en el host.
- **Precondiciones**: Detección no invasiva de servicios de fondo.
- **Archivos Probables**: `layers/l1_nervous/gateway_contract.py`.
- **Tests**: `test_pack_5_2_closure_integrity.py`
- **Done Criteria**: Detección dinámica de puertos locales sin descargas no controladas de modelos.
- **Blast Radius**: Medio.
- **Rollback**: Bypass y uso exclusivo de endpoints en la nube.
- **Plan**: Iniciar de forma diferida.

---

### **PACK 6.0 — Operational CI Full Gate**
*Status*: **DEFERRED**
- **Objetivo**: Integración definitiva de todas las compuertas de seguridad y calidad técnica en el ciclo de integración continua (Specs, Hardening, Tests, Secret-Scan).
- **Precondiciones**: Estabilización total de los bloques de desarrollo.
- **Archivos Probables**: `.github/workflows/ci.yml`.
- **Tests**: Pipeline E2E green completo.
- **Done Criteria**: Ningún commit sin firmas válidas y pruebas E2E 100% exitosas puede ser fusionado.
- **Blast Radius**: Alto.
- **Rollback**: Reducir severidad de advertencias del linter del triage.
- **Plan**: Iniciar Bloque E.

---

### **PACK 6.1 — Minimal Golden Path**
*Status*: **DEFERRED**
- **Objetivo**: Demostración y validación operativa reproducible E2E del flujo completo del motor DUMMIE Engine.
- **Flujo**:
  `query` ➡️ `retrieval` ➡️ `rerank` ➡️ `context package` ➡️ `model route` ➡️ `tool/action` ➡️ `report` ➡️ `memory`
- **Precondiciones**: Integración total de los Packs anteriores de forma contractualmente sólida.
- **Archivos Probables**: `layers/l2_brain/golden_path.py`.
- **Tests**: Pruebas E2E de Golden Path.
- **Métricas Antes/Despues**: Latencia total, precisión del Grounding, tasa de tokens exitosa.
- **Done Criteria**: Un caso de prueba completo y autónomo ejecutando y persistiendo memoria de loci exitosamente sin fallos.
- **Blast Radius**: Máximo (Core del motor).
- **Rollback**: Nulo (Línea de base definitiva de la versión beta).
- **Plan**: Hito de entrega técnica definitivo.
