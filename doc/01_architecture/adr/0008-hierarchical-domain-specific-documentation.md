---
spec_id: "DE-V2-[ADR-008](0008-hierarchical-domain-specific-documentation.md)"
title: "Documentación Modular Jerárquica y Bounded Contexts"
status: "ACTIVE"
version: "1.0.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-[ADR-007](0007-modular-spec-sibling-files.md)"
    relationship: "EXTENDS"
tags: ["architectural_decision", "documentation_hierarchy", "domain_driven_design"]
---

# [ADR-008](0008-hierarchical-domain-specific-documentation.md): Estructura Jerárquica de Especificaciones

## Contexto
El crecimiento de la base de conocimiento del DUMMIE Engine ha generado un desorden en el directorio `doc/specs/`. La presencia de archivos hermanos (.feature, .rules.json) ha triplicado el número de archivos, aumentando el ruido cognitivo para los agentes y dificultando la navegación por capas de soberanía.

## Decisión
Se adopta una estructura de **Directorios por Capas (Bounded Contexts)**. La documentación debe reflejar la arquitectura física del sistema.

### 1. Organización del Filesystem
Las especificaciones se moverán a subdirectorios según su metadata `layer`:
- `doc/specs/L0_Overseer/`: Gobernanza, Orquestación y Topología.
- `doc/specs/L1_Nervous/`: Contratos Protobuf, NATS y Conectividad.
- `doc/specs/L2_Brain/`: Lógica Cognitiva, Memoria y Razonamiento.
- `doc/specs/L3_Shield/`: Seguridad, Validación de Contratos y Shields.
- `doc/specs/L4_Edge/`: Ontologías LST y Procesamiento en el Borde.
- `doc/specs/L5_Muscle/`: Hardware, SIMD y Aceleración.
- `doc/specs/L6_Skin/`: Interfaces de Usuario, Visualización y Telemetría.

### 2. Triada de Soberanía (MSA)
Cada unidad documental debe consistir en:
- `NN_name.md`: Explicación narrativa (Narrativa).
- `NN_name.feature`: Criterios de Aceptación (Ejecutable).
- `NN_name.rules.json`: Reglas de Invariante (Determinista).

### 3. Centralización de ADRs
Para mantener un registro histórico unificado del proyecto, todos los **Architectural Decision Records (ADR)** permanecerán en `doc/adr/`, independientemente de la capa a la que afecten.

## Consecuencias
- **Focus Restricted**: Los agentes pueden restringir su búsqueda a una sola carpeta de capa, reduciendo el consumo de tokens y el riesgo de colisiones semánticas.
- **DDD Compliance**: La documentación ahora es un gemelo digital de la estructura del código.
- **Automatización**: El validador puede imponer reglas de "Capa Correcta" verificando que la ubicación del archivo coincida con su metadata.
