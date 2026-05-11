---
spec_id: "DE-V2-L2-41"
title: "Semantic Fabric Indexer"
status: "ACTIVE"
version: "2.2.0"
layer: "L2"
namespace: "io.dummie.v2.brain.semantic"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L2-39"
    relationship: "REQUIRES"
tags: ["cognitive_core", "documentation_as_code", "lsp"]
---

# 41. Semantic Fabric Indexer (Tejido Semántico)

## Abstract
El Semantic Fabric Indexer actúa como un "Language Server Protocol" (LSP) para la documentación y la memoria del sistema. Garantiza que las entidades definidas en las Especificaciones (`doc/specs`) mantengan enlaces referenciales matemáticamente correctos hacia los ADRs y la memoria semántica. Evita las alucinaciones al forzar la consistencia transversal en el grafo de conocimiento.

## 1. Cognitive Context Model (Ref)
Para los requisitos de referencia cruzada, el manejo de orfandad cognitiva y los estados de gobernanza de los ADRs (Accepted, Superseded), consulte el archivo hermano [41_semantic_fabric_indexer.rules.json](./41_semantic_fabric_indexer.rules.json).

---

## 2. Alcance Operativo
El Indexador se activa ante cualquier mutación en el núcleo arquitectónico (Specs o ADRs):
1.  **Orphan Validation:** Verificación de que no existan referencias colgadas entre documentos.
2.  **Domain Consistency:** Validación de que los términos coincidan con el Lenguaje Ubicuo.
3.  **Governance Auditing:** Si un ADR es marcado como `SUPERSEDED`, el Indexador ignora sus reglas hermanas para evitar conflictos de gobernanza en el Swarm.

---

## 3. Active Constraint Payload
El Indexador consolida todas las reglas activas (`.rules.json`) de los ADRs aceptados y las Specs vigentes en un único payload de restricciones. Este payload es inyectado en cada sesión agéntica para garantizar que el Swarm opere bajo los invariantes de diseño más recientes, eliminando el drift entre la documentación histórica y la ejecución activa.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [41_semantic_fabric_indexer.feature](./41_semantic_fabric_indexer.feature)
- **Machine Rules:** [41_semantic_fabric_indexer.rules.json](./41_semantic_fabric_indexer.rules.json)
