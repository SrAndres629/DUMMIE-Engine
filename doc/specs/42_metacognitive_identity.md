# Spec 42: Metacognitive Identity & Situational Awareness

## 1. Definición
Un agente sin identidad es propenso a la alucinación. Esta spec obliga a que todo proceso cognitivo del DUMMIE Engine comience con la validación de la "Propiocepción Agéntica".

## 2. El Paquete de Identidad
El servidor MCP debe proveer un objeto JSON vía SSH que contenga:
- **Role:** El Locus actual del agente.
- **Constraints:** Limitaciones físicas y de presupuesto (tokens).
- **Causal Anchor:** El ID de sesión vinculado a la Wordline 4D.

## 3. Protocolo de Sincronización
Antes de ejecutar una Directiva, el agente DEBE:
1. Consultar el Oráculo de Contexto (`--whoami`).
2. Validar que su rol es el adecuado para la Capa (L0-L6) en la que va a operar.
3. Registrar el inicio de la tarea en el `ego_state.jsonl`.
