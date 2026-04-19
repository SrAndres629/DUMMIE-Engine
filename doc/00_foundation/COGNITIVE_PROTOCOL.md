# Protocolo de Ingesta y Cristalización Cognitiva (Spec 00)

## 1. Misión: Entropía Cero y Memoria Perpetua
Este protocolo rige cómo los agentes (L2 Brain) deben consumir y generar conocimiento dentro del DUMMIE Engine. Su objetivo es evitar la duplicidad de errores y garantizar la soberanía de la información.

## 2. Procedimiento de Onboarding (Lectura Obligatoria)
Antes de realizar cualquier cambio físico en el monorepo, todo agente DEBE realizar este escaneo secuencial:
1.  **Indexar [ATLAS.md](../ATLAS.md):** Para entender la topología actual del monorepo.
2.  **Escanear [.aiwg/memory/](../../.aiwg/memory/):** 
    -   `decisions.jsonl`: ¿Se ha decidido algo antes sobre este componente?
    -   `lessons.jsonl`: ¿Qué falló la última vez que alguien tocó esto?
    -   `ambiguities.jsonl`: ¿Qué dudas resolvió el PAH recientemente?

## 3. Protocolo de Escritura (Crystallization)
El agente no espera al final de la sesión; cristaliza la memoria en tiempo real tras hitos críticos:

### A. Registro de Decisiones
Si el usuario aprueba un cambio arquitectónico o una implementación Greenfield.
- **Formato:** JSONL alineado con `memory.proto`.
- **Destino:** `.aiwg/memory/decisions.jsonl`.

### B. Registro de Lecciones (Post-Mortem)
Si el agente cometió un error de sintaxis, rompió un test o recibió una corrección del PAH.
- **Formato:** JSONL alineado con `memory.proto`.
- **Destino:** `.aiwg/memory/lessons.jsonl`.

### C. Registro de Ambigüedades
Si el agente tuvo que usar el protocolo `Ask-User-First` para eliminar una indeterminación.
- **Formato:** JSONL alineado con `memory.proto`.
- **Destino:** `.aiwg/memory/ambiguities.jsonl`.

## 4. Invariante de Validación
Cualquier entrada de memoria será validada por el **SDD Auditor (04_forge/sdd_validator.py)**. Las entradas que violen el esquema Protobuf de Layer 1 serán marcadas como `CORRUPTED` y el agente deberá corregirlas mediante auto-reflexión.
