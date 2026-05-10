---
name: "Flujo Cognitivo de Socraticode"
description: "Orquestación obligatoria para el uso de Socraticode antes de mutar la base de código."
version: "1.0.0"
---

# Flujo Cognitivo de Socraticode

Esta Skill define el contrato de comportamiento obligatorio para interactuar con la base de código utilizando Socraticode y DUMMIE Brain. 

## Regla de Oro
**PROHIBIDO** el uso de `cat` o `grep` especulativo para entender conceptos amplios de la base de código. Socraticode es el único sensor autorizado para la fase de descubrimiento semántico.

## Flujo de Trabajo Requerido

### 1. Fase de Percepción (Socraticode)
Antes de proponer o ejecutar un cambio de código, el Agente DEBE seguir este orden:
1. **Búsqueda Semántica:** Ejecutar `codebase_search` con términos conceptuales (ej: "Manejo de sesión de base de datos").
2. **Blast Radius (Análisis de Impacto):** Una vez identificadas las funciones, clases o archivos clave, usar `codebase_impact` (o `codebase_graph_query`) para entender el radio de explosión transitivo de modificar dicho símbolo.
3. **Validación de Ciclos:** Si se están agregando importaciones nuevas, usar `codebase_graph_circular` para prevenir dependencias circulares.

### 2. Fase de Reflexión (DUMMIE Brain)
Con la topología y el radio de impacto descubiertos:
1. Definir los límites de la mutación (Bounded Context).
2. Formular un `IntentDraft` interno y estructurar el cambio.

### 3. Fase de Mutación (Fabricación)
- Ejecutar el cambio usando herramientas de edición específicas (ej: `replace_file_content` o comandos `sed`/escritura aprobados).
- Todas las mutaciones deben respetar los contratos descubiertos en la Fase de Percepción.

### 4. Fase de Cristalización y Observabilidad
- El Gateway generará automáticamente un `MemoryNode4D` en el motor KùzuDB con un `causal_hash`.
- Si experimentas fallos lógicos graves, invoca a `phoenix` (si está disponible como MCP) para inspeccionar las trazas u observar el estado de la saga en el motor L1.

## Excepciones
- `grep_search` solo está permitido cuando se conoce el identificador, cadena de error, o patrón Regex **exacto**. Para conceptos y flujos de arquitectura, el uso de Socraticode es MANDATORIO.
