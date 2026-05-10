---
name: Meta-Gateway Dynamic Discovery
description: Protocolo de descubrimiento y ejecución unificado para TODAS las capacidades del sistema (locales y remotas) vía dummie-brain.
version: 2.0.0
---

# Meta-Gateway Pattern

Para evitar la sobrecarga de la ventana de contexto, el DUMMIE Engine utiliza un **Meta-Gateway Pattern**. Como agente LLM, inicias en estado "Tabula Rasa" (Pizarra en blanco).
No verás docenas de herramientas expuestas. Todo tu cuerpo físico y tus herramientas externas están ocultas detrás de **solo 3 herramientas maestras**.

## Flujo de Trabajo Cognitivo (Workflow)

Cada vez que necesites realizar *cualquier* acción física o lógica (ej. buscar en Git, usar SQLite, o cristalizar conocimiento local), debes seguir este ciclo tridimensional:

### 1. Descubrir Capacidades (Discover)
Si no sabes qué herramientas tienes o qué nombres tienen, usa esta herramienta.
**Herramienta:** `mcp_dummie-brain_dummie_discover_capabilities`
- Puedes pasar un argumento `query` (ej. "git" o "memory") para filtrar.
- Te devolverá una lista de *targets* en formato `local.nombre_herramienta` o `servidor.nombre_herramienta`.

### 2. Analizar Capacidad (Analyze)
Una vez que conoces el `target` exacto (ej. `local.crystallize` o `git.git_status`), descubre qué argumentos exige su contrato.
**Herramienta:** `mcp_dummie-brain_dummie_analyze_capability`
- `target`: Pasa el identificador exacto (ej. "sqlite.read_query").
- Te devolverá el JSON Schema completo y la descripción de la herramienta. **NO adivines argumentos**. Si es la primera vez que usas el target en esta sesión, analízalo.

### 3. Ejecutar Capacidad (Execute)
Ejecuta la herramienta pasando los parámetros mapeados de acuerdo a su Schema.
**Herramienta:** `mcp_dummie-brain_dummie_execute_capability`
- `target`: El identificador (ej. "local.broadcast_intent").
- `arguments`: Un objeto JSON (diccionario) con los parámetros exactos.

---

## ⚠️ Reglas Estrictas de Ejecución
1. **El Target es Sagrado:** Nunca uses espacios o nombres erróneos. Usa siempre el prefijo (`local.` o `server.`).
2. **Cero Suposiciones:** Si un `dummie_execute` falla por "missing arguments" o "validation error", significa que no corriste `dummie_analyze` primero. El SDD (Schema Driven Development) es inquebrantable.
3. **Manejo de SDD Guardrails:** Si `dummie_execute_capability` devuelve un error de `SDD_BLOCKED`, tu acción fue bloqueada por la capa L3 Shield de seguridad Zero-Trust. No insistas sin antes aprobar una especificación (Spec).
