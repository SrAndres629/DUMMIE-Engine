---
spec_id: "DE-V2-L0-43"
title: "Estándares de Documentación y Artefactos"
status: "ACTIVE"
version: "1.0.0"
layer: "L0"
namespace: "io.dummie.v2.governance.docs"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-[ADR-008](../../01_architecture/adr/0008-hierarchical-domain-specific-documentation.md)"
    relationship: "IMPLEMENTS"
tags: ["documentation_standards", "normative", "modular_spec"]
---

# 43. Estándares de Documentación y Artefactos

## Abstract
Para que una **Software Fabrication Engine (SFE)** sea escalable y autónoma, sus planos (Specs) deben seguir un orden industrial riguroso. Esta especificación define los estándares obligatorios de nomenclatura, estructura y jerarquía para toda la documentación del ecosistema DUMMIE Engine y proyectos derivados.

## 1. Topología del Directorio de Specs
Toda especificación debe residir en una carpeta que corresponda a su capa de soberanía:

| Directorio | Capa | Alcance |
| :--- | :--- | :--- |
| `L0_Overseer/` | L0 | Gobernanza, Orquestación, Topología y Estado Global. |
| `L1_Nervous/` | L1 | Conectividad, NATS, Contratos Protobuf y Latidos de Vida. |
| `L2_Brain/` | L2 | Cognición, Razonamiento LLM, Memoria y Grafos de Decisión. |
| `L3_Shield/` | L3 | Seguridad, Invariantes Ejecutables y Shields (Macros S, E, L). |
| `L4_Edge/` | L4 | LST, Ontologías de Código y Procesamiento en el Borde. |
| `L5_Muscle/` | L5 | Hardware, SIMD, VRAM y Cómputo de Alto Rendimiento. |
| `L6_Skin/` | L6 | Interfaces, Visualización de Datos y Telemetría de Usuario. |

---

## 2. Nomenclatura de Archivos (Hermanos MSA)
Cada especificación se compone de una tríada indivisible:

1.  **NN_name.md (Narrativa)**: Archivo principal de contexto.
2.  **NN_name.feature (Ejecutable)**: Escenarios Gherkin con métricas de rendimiento obligatorias.
3.  **NN_name.rules.json (Determinismo)**: Invariantes para el motor de Shield L3.

**Regla de Oro**: El nombre base (NN_name) debe ser idéntico en los tres archivos.

---

## 3. Requisitos de Frontmatter
Todo archivo `.md` y `.feature` basado en SDD V3 debe incluir un header YAML con:
- `spec_id`: Identificador único (ej: `DE-V2-L2-36`).
- `layer`: Capa física (L0-L6).
- `authority`: El rol responsable (ej: `ARCHITECT`).
- `namespace`: Espacio de nombres jerárquico.

---

## 4. Estándar de Métricas de Rendimiento
Dentro de los archivos `.feature`, cada escenario debe incluir al menos una métrica de rendimiento en formato `And Performance Metric: key < value` para facilitar la auditoría automatizada sin parsing de lenguaje natural complejo.

---

## 5. Invariantes de Auditoría
- **Coincidencia Física:** El `sdd_validator.py` rechazará cualquier spec cuyo archivo esté en una carpeta que no coincida con el campo `layer` de su frontmatter.
- **Atomicidad de Hermanos:** No se permite una spec `.md` sin sus hermanos `.feature` y `.rules.json` en capas Alpha (L0, L1).

---

## 6. Soberanía Estructural y No-Redundancia (Axioma de SSOT)
Para garantizar la mantenibilidad y evitar la entropía técnica, se establece el **Axioma de No-Redundancia**:

- **Markdown (.md):** Es la Fuente Semántica de la Verdad para **Humanos**. Debe contener el diseño, los axiomas, la lógica de negocio y la intención arquitectónica. **Prohibido** incluir bloques de código JSON extensos (Cognitive Context Models) si estos ya residen en un archivo `.rules.json`.
- **Machine Rules (.json):** Es el Contrato de Ejecución para **Máquinas**. Contiene la estructura técnica, invariantes y modelos de contexto procesables por el Shield L3.
- **Narrativa Técnica:** En lugar de duplicar el JSON, el archivo Markdown debe proporcionar una **Descripción Funcional** de los parámetros técnicos y apuntar al archivo hermano para la especificación binaria.

**Gobernanza del Error:** Cualquier agente que duplique lógica técnica procesable dentro del archivo narrativo estará cometiendo una falla de "Ingeniería Ciega".
