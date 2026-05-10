---
spec_id: "DE-V2-L4-25"
title: "Registro de Blueprints Industriales"
status: "ACTIVE"
version: "2.2.0"
layer: "L4"
namespace: "io.dummie.v2.edge"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L4-18"
    relationship: "REQUIRES"
tags: ["cognitive_core", "ontology_layer", "industrial_sdd"]
---

# 25. Registro de Blueprints Industriales

## Abstract
El **Registro de Blueprints** es el catálogo maestro de plantillas arquitectónicas del sistema. Este componente almacena los planos inmutables de los nodos atómicos ([Spec 23](../L1_Nervous/23_atomic_modular_nodes.md)), garantizando que cada nueva pieza de software fabricada por el Swarm siga estrictamente los patrones de Diseño Orientado al Dominio (DDD) y Arquitectura Hexagonal.

## 1. Cognitive Context Model (Ref)
Para el backend de almacenamiento (Lloci), el formato de los blueprints (YAML MSA) y los componentes obligatorios de un nodo (Domain, App, Infra), consulte el archivo hermano [25_blueprint_registry.rules.json](./25_blueprint_registry.rules.json).

---

## 2. Anatomía de un Blueprint
Un Blueprint no es solo código; es un manifiesto de intención:
- **Domain Blueprint:** Esquemas puros de negocio y reglas de validación.
- **Application Blueprint:** Use cases, handlers y orquestación de puertos.
- **Infrastructure Blueprint:** Adaptadores físicos y configuraciones de despliegue.

---

## 3. Invariabilidad y Versión
Los blueprints son inmutables una vez registrados:
- **Strict Versioning:** Cualquier modificación genera una nueva versión del blueprint en el registro.
- **No Manual Edit:** El sistema prohíbe la edición manual de los blueprints registrados para prevenir el drift estructural en la fábrica de software.
- **Automatic Hydration:** Cuando el Swarm inicia una tarea de fabricación, el Registro de Blueprints provee el andamiaje (Scaffolding) necesario basándose en el plano seleccionado.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [25_blueprint_registry.feature](./25_blueprint_registry.feature)
- **Machine Rules:** [25_blueprint_registry.rules.json](./25_blueprint_registry.rules.json)
