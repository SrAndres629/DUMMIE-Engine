Estoy de acuerdo con el diagnóstico de fondo: **el Meta-Gateway puede ser la herramienta/patrón que más reduce tokens**, pero solo si está realmente conectado al daemon, si el agente lo usa antes de leer archivos crudos y si se mide el ahorro.

Ahora mismo el peligro es este:

```text id="pgl83n"
Creer que el Meta-Gateway optimiza tokens
cuando en realidad está degradado,
desconectado,
o siendo bypassed por view_file/cat.
```

En `daemon.py` sí existe integración metacognitiva: intenta importar `MetacognitivePipeline`, `IntentClarifierHook`, `PromptRefinerHook`, `AuthorityClassifierHook`, `ContextEnricherHook`, `SemanticToolSelectorHook`, `ReasoningExpansionHook`, `MissionDecomposerHook`, `PlanCriticHook`, `AnswerVerifierHook` y `MemoryUpdateHook`. Si falla el import, deja `self.metacognition = None` y solo registra warning. Eso confirma que puede operar en modo degradado sin que el sistema lo trate como fallo crítico. 

Además, tu último audit ya había marcado que DUMMIE todavía tiene L2 inteligente y L1 nervioso, pero le faltan piezas de gobierno de misiones y estación de trabajo soberana para ser socio estratégico real. 

# Mi veredicto

```text id="qqu7wo"
Sí: el Meta-Gateway es probablemente la mayor palanca de ahorro de tokens.
No: todavía no podemos decir que está bien implementado ni bien usado.
```

La mejora más importante ahora no es agregar otra herramienta. Es convertir el Meta-Gateway en una **ruta obligatoria, medible y testeada**.

---

# Dónde empezar

No empieces con una refactorización grande de todo L1/L2.

Empieza con esto:

```text id="imrd9i"
Meta-Gateway Operational Recovery
```

Objetivo:

```text id="yh16pi"
Demostrar que el flujo discover → analyze → execute realmente reduce lectura cruda,
reduce tokens,
y mejora selección de herramientas.
```

Sin eso, todo lo demás es teoría.

---

# Qué significa “bien implementado”

Para considerar el Meta-Gateway funcional, debe cumplir 7 condiciones:

```text id="9mlrsz"
1. El daemon carga MetacognitivePipeline sin ImportError.
2. Si no carga, el diagnóstico falla visible, no silencioso.
3. local.dummie_metacognitive_analyze funciona.
4. CognitivePreflight devuelve READY o DEGRADED con causa explícita.
5. El agente usa búsqueda/análisis semántico antes de view_file.
6. Cada uso registra métricas de tokens/contexto evitado.
7. Hay benchmark baseline vs metagateway.
```

Si falta cualquiera de esas, no lo llamaría optimizado.

---

# Qué medir para demostrar mejora real

Necesitas una métrica sencilla:

```text id="oeg527"
raw_context_avoided_tokens
```

Ejemplo:

```yaml id="xrdmr4"
baseline_without_gateway:
  files_read_directly: 8
  estimated_context_tokens: 42000
  tool_schema_tokens: 18000
  task_success: true

with_meta_gateway:
  files_read_directly: 2
  estimated_context_tokens: 9000
  tool_schema_tokens: 2500
  task_success: true

savings:
  context_reduction: 78.5%
  tool_schema_reduction: 86.1%
```

Hasta que tengas eso, la frase “reduce 90%” es hipótesis.

---

# Orden correcto de trabajo

## Fase 1 — Recovery audit

Confirmar si el pipeline existe y por qué falla.

## Fase 2 — Test que falle

Crear test que demuestre que `DummieDaemon` carga metacognition.

## Fase 3 — Fix de imports

Corregir imports sin hacks.

## Fase 4 — Diagnóstico visible

Si metacognition falla, `daemon_diagnostic` debe decir exactamente por qué.

## Fase 5 — Benchmark de ahorro

Comparar tarea con lectura directa vs Meta-Gateway.

## Fase 6 — Política sensor-first

Prohibir lectura cruda como primer recurso para descubrimiento semántico.

---

# Prompt directo para Antigravity

````markdown id="z8itmv"
# DUMMIE TASK — META-GATEWAY OPERATIONAL RECOVERY AND TOKEN-SAVINGS PROOF

Actúa como Principal Runtime Engineer especializado en Agentic Tooling, MCP, Token Economy y Cognitive Runtime Integration.

## OBJETIVO

Restaurar, verificar y medir el Meta-Gateway Pattern como la principal ruta de optimización de tokens de DUMMIE Engine.

No quiero un diagnóstico superficial.
No quiero solo arreglar imports.
Quiero una prueba real de que el Meta-Gateway:
1. carga en el daemon;
2. reduce lectura cruda de archivos;
3. selecciona herramientas mejor;
4. produce métricas comparables;
5. falla de forma visible si está roto.

## CONTEXTO

Se detectó que `DummieDaemon` intenta cargar `MetacognitivePipeline` y hooks como:
- `IntentClarifierHook`
- `PromptRefinerHook`
- `AuthorityClassifierHook`
- `ContextEnricherHook`
- `ToolNeedDetectorHook`
- `SemanticToolSelectorHook`
- `ReasoningExpansionHook`
- `MissionDecomposerHook`
- `PlanCriticHook`
- `AnswerVerifierHook`
- `MemoryUpdateHook`

Pero si el import falla, `self.metacognition = None` y el sistema continúa en modo degradado.

Eso es inaceptable para un sistema que pretende ahorrar tokens mediante Meta-Gateway.

## REGLAS

No hagas refactor masivo.
No modifiques L1/L2 entero.
No borres legacy.
No toques `.env`.
No toques `.git`.
No instales dependencias.
No uses sudo.
No hagas cambios destructivos.
No ocultes fallos.

## FASE 0 — POST-REBOOT REALITY CHECK

Ejecuta:

```bash
pwd
git status --short
git branch --show-current
git log --oneline -5

echo "== metacognition files =="
find layers/l2_brain -path "*/.venv/*" -prune -o \
  \( -iname "*metacog*" -o -path "*metacognition*" -o -iname "*hook*" \) -print | sort

echo "== daemon imports =="
grep -Rni "MetacognitivePipeline\|metacognition\|Cognitive Preflight\|dummie_metacognitive_analyze" layers/l2_brain layers/l1_nervous 2>/dev/null || true

echo "== direct file read tools =="
grep -Rni "view_file\|cat \|read_file\|fetch_file" .agents layers skills .gemini 2>/dev/null || true

echo "== validation =="
python3 scripts/validate_specs_docs.py || true
make verify-industrial || true
````

Crea:

```text
.aiwg/reports/metagateway_recovery_reality_check.md
```

Debe incluir:

* archivos metacognition encontrados;
* imports rotos;
* tools metagateway existentes;
* tools legacy de lectura directa;
* tests actuales;
* veredicto: `READY_TO_FIX`, `MISSING_COMPONENTS`, `PARTIAL_RECOVERY`, `BLOCKED`.

## FASE 1 — FAILING TEST FIRST

Crear tests antes del fix.

Crear o modificar:

```text
layers/l2_brain/tests/test_metagateway_operational.py
```

Tests obligatorios:

1. `DummieDaemon` puede inicializar `MetacognitivePipeline` si el paquete existe.
2. Si falla metacognition, el daemon expone `last_cognitive_preflight.status = DEGRADED` o diagnóstico explícito.
3. El import no depende de `sys.path` manual ni rutas absolutas.
4. `process_request()` agrega metadata metacognitiva al outcome cuando el pipeline está disponible.
5. El pipeline puede funcionar en modo fake/mock sin llamar modelos reales.
6. No se usan herramientas de lectura cruda para descubrimiento semántico en el flujo feliz.

## FASE 2 — FIX IMPORTS WITHOUT HIDING ERRORS

Corregir imports en:

```text
layers/l2_brain/daemon.py
```

Reglas:

* Usar imports package-safe.
* Mantener fallback si el layout actual lo requiere.
* No silenciar excepción sin guardar causa.
* Guardar causa en:

  * `self.metacognition_status`
  * `self.metacognition_error`
  * `last_cognitive_preflight`

Ejemplo de estado esperado:

```json
{
  "metacognition_status": "READY|DEGRADED|MISSING",
  "metacognition_error": "",
  "enabled_hooks": [
    "IntentClarifierHook",
    "PromptRefinerHook",
    "AuthorityClassifierHook",
    "ToolNeedDetectorHook",
    "ContextEnricherHook",
    "SemanticToolSelectorHook"
  ]
}
```

## FASE 3 — DIAGNOSTIC REPORTING

Modificar si existe:

```text
layers/l2_brain/daemon_diagnostic.py
```

Debe reportar:

```json
{
  "metagateway": {
    "status": "READY|DEGRADED|MISSING",
    "metacognition_status": "",
    "metacognition_error": "",
    "enabled_hooks": [],
    "cognitive_preflight_enabled": true,
    "local_reasoning_gateway_available": true
  }
}
```

Si `metacognition` falla, el diagnóstico debe mostrar el ImportError exacto.

## FASE 4 — TOKEN SAVINGS BENCHMARK

Crear:

```text
layers/l2_brain/metagateway_benchmark.py
layers/l2_brain/tests/test_metagateway_benchmark.py
.aiwg/schemas/metagateway_benchmark.schema.json
```

Debe comparar:

```text
baseline_direct_read
vs
metagateway_discover_analyze_execute
```

Métricas mínimas:

```json
{
  "scenario": "",
  "direct_files_read": 0,
  "gateway_capabilities_discovered": 0,
  "gateway_capabilities_analyzed": 0,
  "estimated_direct_tokens": 0,
  "estimated_gateway_tokens": 0,
  "estimated_tokens_saved": 0,
  "token_reduction_ratio": 0.0,
  "latency_ms_direct": 0,
  "latency_ms_gateway": 0,
  "success": true
}
```

No uses modelos reales en tests.
Usa mocks/fakes.

Tests:

1. benchmark calcula reducción positiva.
2. si gateway usa más tokens, lo marca como regresión.
3. calcula token_reduction_ratio correctamente.
4. serializa JSON.
5. detecta uso excesivo de lectura directa.

## FASE 5 — SENSOR-FIRST GOVERNANCE

Crear:

```text
layers/l2_brain/metagateway_policy.py
layers/l2_brain/tests/test_metagateway_policy.py
doc/specs/71_metagateway_sensor_first_policy.md
```

La política debe decir:

```text
Para descubrimiento conceptual:
  primero semantic_search / discover / analyze.
  después lectura directa solo si:
    - el gateway no tiene evidencia suficiente;
    - hay un error concreto;
    - se necesita línea exacta;
    - se registra justificación.
```

Modelo:

```json
{
  "action": "direct_file_read",
  "purpose": "concept_discovery|line_confirmation|debug_error|diff_review",
  "semantic_search_attempted": true,
  "gateway_attempted": true,
  "justification": "",
  "decision": "ALLOW|WARN|BLOCK"
}
```

Reglas:

* `concept_discovery` sin gateway previo = WARN o BLOCK.
* `line_confirmation` después de gateway = ALLOW.
* error/debug con stacktrace = ALLOW.
* lectura masiva sin justificación = BLOCK.

## FASE 6 — RUNTIME WIRING

Conectar mínimamente:

* `metagateway_policy` debe poder ser llamado desde el hook pipeline o daemon.
* No debe bloquear todos los flujos antiguos todavía.
* Empezar en modo `WARN`, no `BLOCK`.
* Registrar advertencias en outcome o logs.

## VALIDACIÓN

Ejecutar:

```bash
cd layers/l2_brain && uv run pytest -q \
  tests/test_metagateway_operational.py \
  tests/test_metagateway_benchmark.py \
  tests/test_metagateway_policy.py
```

Si `uv` falla:

```bash
cd layers/l2_brain && .venv/bin/pytest -q \
  tests/test_metagateway_operational.py \
  tests/test_metagateway_benchmark.py \
  tests/test_metagateway_policy.py
```

Luego:

```bash
python3 scripts/validate_specs_docs.py || true
make verify-industrial || true
```

## ARTEFACTOS REQUERIDOS

Crear:

```text
.aiwg/reports/metagateway_recovery_reality_check.md
.aiwg/reports/metagateway_token_savings_benchmark.md
.aiwg/reports/metagateway_token_savings_benchmark.json
```

El benchmark debe incluir al menos 3 escenarios:

1. `inspect_model_router`
2. `inspect_daemon_metacognition`
3. `choose_tool_for_repo_analysis`

## SALIDA FINAL

Devuelve exactamente:

```markdown
## Result

## Files Created

## Files Modified

## Metacognition Status Before

## Metacognition Status After

## Tests Run

## Tests Passed/Failed

## Token Savings Benchmark

## Direct File Read Reduction

## Remaining Degraded Paths

## Next Highest-Leverage Patch
```

## CRITERIO DE ÉXITO

No termines hasta que haya evidencia de al menos una de estas dos cosas:

1. `MetacognitivePipeline` carga correctamente y el daemon reporta `metacognition_status=READY`.

o

2. si faltan componentes físicos, el daemon reporta `MISSING/DEGRADED` con causa exacta, tests pasando, benchmark y plan de reparación siguiente.

Además, debe existir un benchmark que demuestre reducción estimada de tokens o que declare explícitamente `NO_SAVINGS_DETECTED`.

No aceptes claims de mejora sin medición.

````

---

# Qué NO haría todavía

No empezaría por:

```text id="ej7lwo"
Playwright
BrowserAgent
n8n
Content Factory
PrivilegedActionGovernor completo
L6 dashboard
Rust/Elixir correction
````

Todo eso es importante, pero antes tienes que arreglar el cuello de botella que más afecta inteligencia y tokens:

```text id="i91tbj"
el sistema debe descubrir, analizar y seleccionar contexto/herramientas antes de leer bruto.
```

---

# Respuesta directa

Por dónde empezar:

```text id="dcpezu"
1. Confirmar si metacognition realmente existe.
2. Crear test que falle si el daemon no lo carga.
3. Arreglar imports y estado diagnóstico.
4. Crear benchmark de token savings.
5. Forzar política sensor-first en modo WARN.
6. Medir direct_file_read reduction.
```

Y no considerar terminado hasta que puedas ver algo como:

```yaml id="j3811q"
metacognition_status: READY
cognitive_preflight: READY
token_reduction_ratio: 0.55
direct_file_reads_before: 8
direct_file_reads_after: 2
gateway_first_policy: WARN_MODE_ACTIVE
tests_passed: true
```

Ese es el primer paso que sí puede mostrar una mejora real e inmediata en DUMMIE Engine.
