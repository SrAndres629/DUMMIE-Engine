---
spec_id: "DE-V2-[ADR-007](0007-modular-spec-sibling-files.md)"
title: "Arquitectura de Especificaciones Modulares (MSA) y Archivos Hermanos"
status: "ACTIVE"
version: "1.0.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L3-22"
    relationship: "IMPLEMENTS"
  - id: "DE-V2-[ADR-006](0006-sovereign-hybrid-documentation-protocol.md)"
    relationship: "EXTENDS"
tags: ["architectural_decision", "modular_specs", "bdd_automation"]
---

# [ADR-007](0007-modular-spec-sibling-files.md): Modular Spec Assembly (MSA)

## Abstract
La mezcla de narrativa visionaria y lógica técnica en un solo archivo aumenta la entropía y el consumo de tokens. Esta decisión establece el estándar **Modular Spec Assembly (MSA)**, descomponiendo cada especificación en una tríada de archivos (Markdown, Feature, Rules) para facilitar el testeo automatizado y la eficiencia cognitiva.

## 1. Cognitive Context Model (Ref)
Para la definición de los componentes de la tríada (.md, .feature, .rules.json), los beneficios de eficiencia de tokens y los invariantes de mantenimiento, consulte el archivo hermano [0007-modular-spec-sibling-files.rules.json](./0007-modular-spec-sibling-files.rules.json).

---

## 2. Contexto
Las especificaciones en un solo archivo `.md` mezclan narrativa humana con lógica técnica densa, lo que aumenta el consumo de tokens y dificulta la automatización del testeo BDD (Behavior-Driven Development). Los agentes necesitan una forma rápida de extraer los **Criterios de Aceptación** y las **Reglas de Invariante** sin procesar todo el contexto visionario.

---

## 3. Decisión
Se adopta la arquitectura **Modular Spec Assembly (MSA)**. Cada especificación se descompone en tres archivos hermanos ubicados en el mismo directorio:

### 3.1 El Manifiesto Narrativo (`XX_name.md`)
- **Contenido**: Visionario, descriptivo, diagramas y contexto arquitectónico.
- **Consumidor**: Arquitectos Humanos y Agentes de Fase de Diseño.

### 3.2 El Contrato Ejecutable (`XX_name.feature`)
- **Contenido**: Escenarios Gherkin (Given/When/Then) que definen los Criterios de Aceptación (AC).
- **Métricas**: Define los baselines de rendimiento (latencia, VRAM, tokens).

### 3.3 El Archivo de Invariantes (`XX_name.rules.json`)
- **Contenido**: Reglas deterministas para el Shield L3 (Rust), basadas en el esquema de la Spec 22.
- **Consumidor**: Shields de Seguridad y Motores de Validación Programática.

---

## 4. Protocolo de Mantenimiento
- **Auto-Generación**: El `sdd_validator.py` tiene la potestad de generar plantillas vacías para los archivos hermanos si detecta que faltan.
- **Indivisibilidad**: Cualquier cambio en la lógica de la Spec `.md` debe sincronizarse inmediatamente con sus hermanos.

---

## 5. Consecuencias
- **Eficiencia de Tokens**: Reducción del ~40% en el consumo de tokens.
- **Determinismo**: Mejora en la precisión del código generado al tener ACs inequívocos.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** `0007-modular-spec-sibling-files.feature`
- **Machine Rules:** `0007-modular-spec-sibling-files.rules.json`
