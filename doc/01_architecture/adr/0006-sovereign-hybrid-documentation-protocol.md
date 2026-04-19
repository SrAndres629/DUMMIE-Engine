---
spec_id: "DE-V2-[ADR-006](0006-sovereign-hybrid-documentation-protocol.md)"
title: "Protocolo de Ejecución Híbrida Soberana y Documentación en Tiempo Real"
status: "ACTIVE"
version: "1.0.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-[ADR-005](0005-cognitive-fabrication-protocols.md)"
    relationship: "EXTENDS"
  - id: "DE-V2-L0-08"
    relationship: "IMPLEMENTS"
tags: ["architectural_decision", "hybrid_execution", "documentation_integrity"]
---

# [ADR-006](0006-sovereign-hybrid-documentation-protocol.md): Ejecución Híbrida y Verdad Física

## Contexto
El sistema DUMMIE Engine se basa en la **Hermeticidad Políglota (Spec 08)**. Sin embargo, la ausencia de Nix en ciertos entornos de desarrollo (Host) genera una ambigüedad operativa. Los agentes han demostrado una tendencia a la "amnesia de entorno" y a la "alucinación de progreso", reportando componentes como terminados cuando solo son esqueléticos.

## Decisión
Se establecen tres pilares fundamentales para la operación del Swarm:

### 1. Modelo de Ejecución Híbrida Soberana
Para maximizar la velocidad sin comprometer la hermeticidad:
- **Builds Polyglot (L0, L1, L3, L4, L5):** Se delega exclusivamente a **Docker** (`Dockerfile.builder`). Ningún agente intentará compilar Go, Elixir, Rust o Zig localmente si el entorno Nix no está activo.
- **Cognición y Diseño (L2, Docs, JSON):** Se permite el uso de herramientas locales (como `uv` para Python y editores de Markdown) para agilizar el ciclo de razonamiento y actualización de Specs.

### 2. Principio de Alineación con la Verdad Física
Se prohíbe el desajuste entre la documentación y el estado real del código:
- Si un componente es esquelético, la documentación **DEBE** reflejarlo como "Skeletal" o "In Progress".
- Queda terminantemente prohibido marcar hitos como "FINALIZADOS" en el `README.md` o `AGENTS.md` si el código no ha pasado la validación del Sentinel.

### 3. Protocolo de Documentación Proactiva
La documentación no es un proceso post-hoc; es el sistema mismo.
- **Actualización en Tiempo Real:** Todo aprendizaje, resolución de ambigüedad o decisión técnica debe registrarse en la memoria de sesión (`.aiwg/memory/`) y en las Specs pertinentes **antes** de dar por terminada una tarea.
- **Autonomía Documental:** Los agentes tienen el mandato de corregir inconsistencias en la documentación base (`README.md`, `AGENTS.md`) tan pronto como las detecten, sin esperar instrucciones explícitas.

## Consecuencias
- **Eliminación del Drift:** La documentación siempre será un reflejo fiel del potencial físico del sistema.
- **Portabilidad:** El uso de Docker garantiza que la SFE (Software Fabrication Engine) pueda arrancar en cualquier host con soporte para contenedores.
- **Consistencia:** Los agentes entrantes tendrán un mapa claro de "qué falta" y "qué se ha decidido".
