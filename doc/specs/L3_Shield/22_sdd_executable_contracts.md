---
spec_id: "DE-V2-L3-22"
title: "Contratos Ejecutables de Gobernanza (SDD)"
status: "ACTIVE"
version: "2.2.0"
layer: "L3"
namespace: "io.dummie.v2.shield"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L1-10"
    relationship: "REQUIRES"
tags: ["cognitive_core", "security_layer", "industrial_sdd"]
---

# 22. Contratos Ejecutables de Gobernanza (SDD)

## Abstract
Los **Contratos Ejecutables** son la materialización física de las especificaciones SDD en Layer 3. Estos contratos actúan como "Architectural Fitness Functions" que validan cada transacción cognitiva contra los invariantes definidos en los archivos `.rules.json`, garantizando que el sistema nunca derive hacia estados de desorden o deuda técnica.

## 1. Cognitive Context Model (Ref)
Para el directorio de reglas de gobernanza, los modos de cumplimiento (Strict Block, Warn) y los requisitos de persistencia mediante AF_TOKEN, consulte el archivo hermano [22_sdd_executable_contracts.rules.json](./22_sdd_executable_contracts.rules.json).

---

## 2. Inyección de Restricciones
El Escudo L3 inyecta las restricciones en el tiempo de ejecución:
1.  **Contract Loading:** Carga de los archivos `.rules.json` asociados a la tarea activa.
2.  **Inference Interception:** Análisis del `Thought Vector` y la `Action` propuesta por el Swarm.
3.  **Fitness Check:** Evaluación de si la acción viola algún invariante estructural o de gobernanza.

---

## 3. Prevención de Drift de Código
Los contratos ejecutables prohíben la edición manual de archivos críticos:
- **Hash Integrity:** Validación periódica de los hashes de los archivos de gobernanza.
- **Strict Enforcement:** Cualquier intento de modificar las reglas sin seguir el flujo SDD bloquea el acceso de escritura al monorepo hasta que el Auditor L2 resuelva el conflicto.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [22_sdd_executable_contracts.feature](./22_sdd_executable_contracts.feature)
- **Machine Rules:** [22_sdd_executable_contracts.rules.json](./22_sdd_executable_contracts.rules.json)
