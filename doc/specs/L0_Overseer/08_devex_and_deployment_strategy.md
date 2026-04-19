---
spec_id: "DE-V2-L0-08"
title: "DevEx y Estrategia de Despliegue Hermético"
status: "ACTIVE"
version: "2.1.0"
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

## 1. Cognitive Context Model (JSON)
```json
{
  "environment": {
    "tool": "Nix Flakes",
    "isolation": "Hermetic (No Global Pkgs)",
    "entrypoint": "nix develop"
  },
  "deployment": {
    "orchestration": "Master Makefile",
    "components": [
      "Atomic Build",
      "Zero-Install Workflow",
      "Fast Startup"
    ]
  },
  "observability": {
    "standard": "OpenTelemetry ([Spec 13](../L6_Skin/13_observability_opentelemetry.md))",
    "correlation": "Trace-ID via NATS/Arrow"
  },
  "invariants": [
    "No Manual Steps",
    "Hardware Sanity Check Before Boot"
  ],
  "personality_ref": "DE-V2-L0-33",
  "ledger_link": "DE-V2-L2-34"
}
```

---

## 2. Hermeticidad de Entorno (Nix Flakes)
Para erradicar el "funciona en mi máquina", el sistema prohíbe el uso de gestores de paquetes globales.
- **SSoT de Dependencias:** El archivo `flake.nix` nativo en la raíz es la única fuente de verdad para binarios, compiladores (Go, Rust, Zig) y runtimes (Python, Elixir, Mojo).
- **Zero-Install Workflow:** El desarrollador accede al entorno completo mediante `nix develop`, garantizando que todas las capas (L0-L6) posean versiones de librerías nativas (libarrow, CUDA) 100% compatibles.

---

## 3. Despliegue de Comando Único (One-Click)
La orquestación de la compilación y el arranque está centralizada en un **Master Makefile**:
- **Atomic Build:** Un solo comando compila los bindings de Rust (PyO3), genera stubs de Protobuf, prepara el Bus NATS y levanta el Árbitro de Elixir.
- **Fast Startup:** El sistema utiliza cache dinámico de Nix para evitar re-compilaciones innecesarias, permitiendo un arranque del ecosistema completo en < 30 segundos.

---

## 4. Trazabilidad Políglota (Zero-Blindness)
- **Unified Observability:** Integración obligatoria con OpenTelemetry ([Spec 13](../L6_Skin/13_observability_opentelemetry.md)).
- **Trace Correlation:** Cada saga posee un `trace_id` inyectado en los headers de NATS y metadatos de Arrow, permitiendo visualizar el flujo de datos entre lenguajes sin saltos de contexto.

---

## 6. Compromisos de Runtime (Estrategia de Transición)
Debido a restricciones específicas del host o la cadena de herramientas políglota, se han adoptado los siguientes compromisos pragmáticos que actúan como extensiones de esta Spec:

### 6.1. Enclave de Compilación Soberano (Docker Builder)
- **Mecanismo**: El archivo `Dockerfile.builder` es la **Fuente Única de Verdad** del runtime políglota (Go 1.23+, Elixir 1.16, Zig 0.11, Rust, Python 3.11).
- **Justificación**: Provee un entorno hermético e idéntico para todos los agentes, independientemente de la configuración de Nix del host.
- **Protocolo**: Toda compilación y generación de stubs DEBE ejecutarse mediante el contenedor `dummie-builder`.

### 6.2. Estrategia de Descarga de Dependencias (Unidad D)
- **Política**: Todo artefacto derivado o "bloatware" (venvs, caches de Go/Mix, node_modules) superior a 50MB DEBE residir en la **Unidad D (/media/datasets)**.
- **Implementación**: Uso mandatorio de enlaces simbólicos (symlinks) desde el monorepo hacia `/media/datasets/dummie/`.
- **Invariante**: El monorepo en la unidad principal debe mantenerse ligero (< 500MB) para optimizar la indexación y el razonamiento de los agentes.

### 6.3. Sincronización de Permisos
- **Regla**: Tras cada operación de construcción en el enclave Docker, el agente ejecutor DEBE restaurar la propiedad de los archivos al usuario del host (`chown`) para evitar bloqueos de integridad.
