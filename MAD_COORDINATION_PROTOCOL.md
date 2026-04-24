# PROTOCOLO DE COORDINACIÓN MULTI-AGENTE (MAD v2.5)

Este documento establece las reglas de convivencia para los agentes que operan simultáneamente en el proyecto (Antigravity, Codex, Gemini CLI, etc.).

## 1. El Ledger de Enjambre (SSoT)
El archivo `.aiwg/memory/swarm_ledger.jsonl` es la fuente única de verdad sobre la actividad actual.
- **REGLA DE ORO**: Antes de iniciar una tarea, un agente DEBE consultar `observe_swarm`.
- **REGLA DE ACCIÓN**: Antes de escribir/modificar archivos, un agente DEBE llamar a `broadcast_intent`.

## 2. Gestión de Conflictos (Atomic Locking)
- Si dos agentes intentan modificar el mismo `target`, el agente con el **Lamport Clock** más bajo debe ceder o esperar a que el otro termine.
- Si un agente detecta que otro está trabajando en el mismo componente, debe abrir un canal de "Sugerencia" (Lesson Log) en lugar de sobrescribir.

## 3. Niveles de Permiso
- **Nivel L0 (Solo Lectura)**: Observación del estado.
- **Nivel L1 (Colaboración)**: Edición de archivos con broadcast previo.
- **Nivel L2 (Orquestación)**: Modificación de infraestructura y coordinación de sub-agentes.

## 4. Mitigación de Sandbox (bwrap)
Si un agente CLI encuentra un error `Errno 1` (Operation not permitted):
1. Reportar el bloqueo mediante `log_lesson`.
2. Solicitar al usuario humano (Authority A) la elevación de privilegios o relajación del sandbox.
3. Degradar a modo "Offline" para tareas que no requieran red.

---
**[PROVISIÓN DE SOBERANÍA]**: Todo agente que siga este protocolo tiene permiso para proponer cambios y criticar los planes de otros agentes en el ledger de decisiones.
