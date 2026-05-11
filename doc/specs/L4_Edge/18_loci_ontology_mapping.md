---
spec_id: "DE-V2-L4-18"
title: "Palacio de Loci y RBAC Topográfico"
status: "ACTIVE"
version: "2.2.0"
layer: "L4"
namespace: "io.dummie.v2.edge"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L2-02"
    relationship: "REQUIRES"
tags: ["cognitive_core", "ontology_layer", "industrial_sdd"]
---

# 18. Palacio de Loci y RBAC Topográfico

## Abstract
El **Palacio de Loci** es el mapa tridimensional del monorepo. Utilizando un escáner de alto rendimiento escrito en Zig, este componente genera un Grafo de Conocimiento (LST) que reside en KùzuDB. Layer 4 garantiza que cada agente tenga una visión topográfica precisa del sistema, aplicando un Control de Acceso Basado en Roles (RBAC) que limita la visibilidad del código según el Bounded Context de la tarea.

## 1. Cognitive Context Model (Ref)
Para el motor de escaneo (Zig LST), los símbolos requeridos (Path, Hash, Type) y los invariantes de sincronización en tiempo real con la base de datos de grafos, consulte el archivo hermano [18_loci_ontology_mapping.rules.json](./18_loci_ontology_mapping.rules.json).

---

## 2. Escaneo LST (Latent Semantic Tree)
El Palacio de Loci trasciende el LST tradicional mediante el uso de un grafo semántico:
- **Latent Mapping:** Indexación no solo de la sintaxis, sino de las relaciones semánticas transversales entre Specs, Código y ADRs.
- **Topographical RBAC:** Los agentes no ven archivos; ven "Loci" (lugares) con permisos de lectura/escritura definidos por su rol en el Swarm.

---

## 3. Sincronización Invariante
Toda edición física en el monorepo activa un **Re-indexing Event**:
1.  **Detection:** Layer 4 detecta el cambio de hash en un archivo.
2.  **Partial Scan:** El escáner de Zig actualiza solo el nodo afectado y su radio de explosión.
3.  **Graph Update:** Los cambios se proyectan en KùzuDB para que el Cerebro L2 tenga una visión actualizada de la Verdad Física.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [18_loci_ontology_mapping.feature](./18_loci_ontology_mapping.feature)
- **Machine Rules:** [18_loci_ontology_mapping.rules.json](./18_loci_ontology_mapping.rules.json)
