---
spec_id: "DE-V2-L0-08"
title: "DevEx y Estrategia de Despliegue Hermético"
status: "ACTIVE"
version: "2.2.0"
layer: "L0"
namespace: "io.dummie.v2.devex"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L0-11"
    relationship: "IMPLEMENTS"
tags: ["cognitive_core", "devex_strategy", "industrial_sdd"]
---

# 08. DevEx y Estrategia de Despliegue Hermético

## Abstract
La adopción de una arquitectura políglota de 7 capas introduce una fricción operativa crítica. Esta especificación define los mecanismos de abstracción para garantizar que el sistema sea desplegable mediante un **Comando Único**, eliminando la complejidad accidental mediante la hermeticidad de dependencias y la automatización implacable del entorno.

## 1. Cognitive Context Model (Ref)
Para el entorno de herramientas (Nix, Docker), los componentes de despliegue y los invariantes de trazabilidad políglota (OpenTelemetry), consulte el archivo hermano [08_devex_and_deployment_strategy.rules.json](./08_devex_and_deployment_strategy.rules.json).

---

## 2. Hermeticidad de Entorno (Nix Flakes)
Para erradicar el "funciona en mi máquina", el sistema prohíbe el uso de gestores de paquetes globales.
- **SSoT de Dependencias:** El archivo `flake.nix` nativo en la raíz es la única fuente de verdad para binarios, compiladores (Go, Rust, Zig) y runtimes (Python, Elixir, Mojo).
- **Zero-Install Workflow:** El desarrollador accede al entorno completo mediante `nix develop`.

---

## 3. Despliegue de Comando Único (One-Click)
La orquestación de la compilación y el arranque está centralizada en un **Master Makefile**:
- **Atomic Build:** Un solo comando compila bindings, genera stubs de Protobuf, prepara NATS y levanta Elixir.
- **Fast Startup:** Uso de cache dinámico de Nix para arranque en < 30 segundos.

---

## 4. Trazabilidad Políglota (Zero-Blindness)
- **Unified Observability:** Integración obligatoria con OpenTelemetry ([Spec 13](../L6_Skin/13_observability_opentelemetry.md)).
- **Trace Correlation:** Cada saga posee un `trace_id` inyectado en headers de NATS y metadatos de Arrow.

---

## 5. Compromisos de Runtime (Estrategia de Transición)

### 5.1. Enclave de Compilación Soberano (Docker Builder)
- **Mecanismo**: `Dockerfile.builder` es la **Fuente Única de Verdad** del runtime políglota.
- **Protocolo**: Toda compilación y generación de stubs DEBE ejecutarse mediante el contenedor `dummie-builder`.

### 5.2. Estrategia de Descarga de Dependencias (Unidad D)
- **Política**: Todo artefacto derivado o "bloatware" (> 50MB) DEBE residir en la **Unidad D (/media/datasets)**.
- **Implementación**: Uso mandatorio de enlaces simbólicos (symlinks) hacia `/media/datasets/dummie/`.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [08_devex_and_deployment_strategy.feature](./08_devex_and_deployment_strategy.feature)
- **Machine Rules:** [08_devex_and_deployment_strategy.rules.json](./08_devex_and_deployment_strategy.rules.json)
