---
skill_id: "sw.arch.diagram_generator"
name: "Orquestador de Diagramas C4/Mermaid"
version: "1.0.0"
description: "Generador autónomo de visualizaciones arquitectónicas basadas en el Palacio de Loci."
author: "DUMMIE Engine-SFE"
capabilities:
  - "AUTO_LAYOUT"
  - "C4_COMPLIANCE"
  - "LOCI_INTEGRATION"
requirements:
  layers: ["L2", "L4"]
  tools: ["mermaid-cli", "plantuml", "kuzu-query"]
invariants:
  - "diagram_syntax_valid: true"
  - "forbidden_labels: blocked"
  - "traceability: causal"
---

# Skill: Diagram Generator (sw.arch.diagram_generator)

## Propósito
Esta habilidad permite a los agentes del DUMMIE Engine generar visualizaciones arquitectónicas precisas, dinámicas y estéticamente superiores (`premium aesthetics`) para documentar el estado del sistema.

## Protocolo de Uso
1. **Ingesta:** El agente recibe una descripción técnica o consulta el grafo de Loci.
2. **Abstracción:** Se mapean los componentes al modelo C4.
3. **Renderizado:** Se genera el código Mermaid cumpliendo con los invariantes de `rules.json`.
4. **Validación:** El Sentinel (L3) verifica que no haya etiquetas prohibidas.
5. **Persistencia:** Se guarda el diagrama y se registra la ejecución en `ledger.jsonl`.

## Capacidades Premium
- Soporte para Glassmorphism en diagramas SVG.
- Temas oscuros por defecto alineados con el diseño del motor.
- Trazabilidad causal total.
