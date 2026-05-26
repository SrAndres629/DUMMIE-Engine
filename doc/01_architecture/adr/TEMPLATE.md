---
spec_id: DE-V2-L0-ADR-XXX
title: '[Título Breve e Imperativo]'
status: PROPOSED
version: 1.0.0
layer: L0
namespace: io.dummie.v2.adr
authority: ARCHITECT
claims:
- id: TEMPLATE-file-valid
  description: Spec file 'TEMPLATE.md' exists, parses valid YAML frontmatter, and
    is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/01_architecture/adr/TEMPLATE.md').read().split('---')[1]); assert d,
    'empty frontmatter'"
  severity: critical
---
# ADR-XXXX: [Título Breve e Imperativo]

## Contexto y Problema
Describe el problema técnico o de negocio que estamos intentando resolver. ¿Cuál es el "dolor" que justifica esta decisión?

## Decisión Arquitectónica
Describe la solución elegida de forma clara. Qué vamos a hacer.

## Consecuencias
Describe qué pasa ahora que tomamos esta decisión.
- **Positivas:** Qué ganamos.
- **Negativas/Restricciones:** Qué perdemos o a qué nos obliga esta decisión.

---

## [MSA] Sibling Components Requeridos
Todo ADR debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** `XXXX-nombre-adr.feature` (Prueba de integración de la consecuencia)
- **Machine Rules:** `XXXX-nombre-adr.rules.json` (Restricción matemática que el validador forzará)
