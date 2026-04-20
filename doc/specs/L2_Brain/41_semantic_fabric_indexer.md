---
spec_id: "DE-V2-L2-41"
title: "Semantic Fabric Indexer"
status: "ACTIVE"
version: "1.0.0"
layer: "L2"
namespace: "io.dummie.v2.brain.semantic"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L2-39"
    relationship: "REQUIRES"
tags: ["cognitive_core", "documentation_as_code", "lsp"]
---

# Semantic Fabric Indexer (Tejido Semántico)

## Abstract
El Semantic Fabric Indexer actúa como un "Language Server Protocol" (LSP) para la documentación y la memoria del sistema. Garantiza que las entidades definidas en las Especificaciones (`doc/specs`) mantengan enlaces referenciales matemáticamente correctos hacia los Architectural Decision Records (`doc/01_architecture/adr`) y la memoria semántica (`.aiwg/memory`). Evita las alucinaciones al forzar la consistencia transversal.

## 1. Alcance Operativo
El Indexador entra en acción cada vez que el `sw.arch.core` crea o modifica una Spec o un ADR. 
1. Analiza los identificadores (ej. IDs de Specs, IDs de Resolución) y valida que no existan "referencias colgadas" u "orfandad cognitiva". 
2. Si detecta un término de dominio, verifica que coincida con el Lenguaje Ubicuo general del repositorio.
3. **Auditoría Activa de ADRs:** Escanea `doc/01_architecture/adr/`. Si un ADR tiene `status: SUPERSEDED`, el Indexador ignora matemáticamente sus archivos `.rules.json` y `.feature` hermanos para evitar conflictos de gobernanza. Si el ADR está `ACCEPTED`, sus reglas se consolidan en el "Active Constraint Payload" del enjambre.

---

## [MSA] Sibling Components
- **Executable Contract**: 41_semantic_fabric_indexer.feature
- **Machine Rules**: 41_semantic_fabric_indexer.rules.json
