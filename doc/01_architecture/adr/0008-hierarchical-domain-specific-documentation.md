---
spec_id: "DE-V2-[ADR-008](0008-hierarchical-domain-specific-documentation.md)"
title: "Documentación Modular Jerárquica y Bounded Contexts"
status: "ACTIVE"
version: "1.1.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-[ADR-007](0007-modular-spec-sibling-files.md)"
    relationship: "EXTENDS"
tags: ["architectural_decision", "documentation_hierarchy", "domain_driven_design"]
---

# [ADR-008](0008-hierarchical-domain-specific-documentation.md): Estructura Jerárquica de Especificaciones

## Abstract
El crecimiento de la base de conocimiento del DUMMIE Engine requiere una organización que respete la topología física del sistema. Esta decisión adopta una estructura de **Directorios por Capas (Bounded Contexts)**, alineando la documentación con la arquitectura políglota de 7 capas para reducir el ruido cognitivo y facilitar la validación automatizada.

## 1. Cognitive Context Model (Ref)
Para el mapeo de directorios por capa y los invariantes de validación de rutas, consulte el archivo hermano [0008-hierarchical-domain-specific-documentation.rules.json](./0008-hierarchical-domain-specific-documentation.rules.json).

---

## 2. Contexto
La presencia de archivos hermanos (.feature, .rules.json) ha triplicado el número de archivos, aumentando el ruido cognitivo para los agentes y dificultando la navegación por capas de soberanía. Se requiere un orden industrial que segregue las responsabilidades por dominio.

---

## 3. Decisión: Organización por Bounded Contexts
Se adopta una estructura de **Directorios por Capas**. La documentación debe reflejar la arquitectura física del sistema.

### 3.1 Organización del Filesystem
Las especificaciones residen en subdirectorios según su metadata `layer`:
- `doc/specs/L0_Overseer/`: Gobernanza y Orquestación.
- `doc/specs/L1_Nervous/`: Conectividad y Contratos.
- `doc/specs/L2_Brain/`: Lógica Cognitiva y Memoria.
- `doc/specs/L3_Shield/`: Seguridad e Invariantes.
- `doc/specs/L4_Edge/`: Ontologías LST.
- `doc/specs/L5_Muscle/`: Hardware y Aceleración.
- `doc/specs/L6_Skin/`: Interfaces y Telemetría.

### 3.2 Centralización de ADRs
Todos los **Architectural Decision Records (ADR)** permanecerán en `doc/01_architecture/adr/`, independientemente de la capa a la que afecten, para mantener un registro histórico unificado.

---

## 4. Consecuencias
- **Focus Restricted**: Los agentes pueden restringir su búsqueda a una sola carpeta de capa.
- **DDD Compliance**: La documentación es un gemelo digital de la estructura del código.
- **Automatización**: El validador impone reglas de "Capa Correcta" verificando el match entre ruta y frontmatter.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [0008-hierarchical-domain-specific-documentation.feature](./0008-hierarchical-domain-specific-documentation.feature)
- **Machine Rules:** [0008-hierarchical-domain-specific-documentation.rules.json](./0008-hierarchical-domain-specific-documentation.rules.json)
