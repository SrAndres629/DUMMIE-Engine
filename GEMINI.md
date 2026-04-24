# METODOLOGÍA MULTI-AGENTE DUMMIE (MAD) - VERSION 2026

Este proyecto utiliza una metodología de trabajo multi-agente de alta precisión basada en el rigor de **Specs Driven Development (SDD)**.

## 1. El Nuevo Equipo de Agentes (SDD Edition)
El desarrollo se delega en 5 agentes especializados con soberanía sobre su Locus:

1.  **`contract-architect` (Locus: Spec):** El guardián de la verdad. Diseña, audita y evoluciona los contratos (OpenAPI, Proto, Zod). Nada se construye sin su esquema aprobado.
2.  **`behavior-synth` (Locus: TDD/BDD):** El traductor de intenciones. Transforma las specs en escenarios Gherkin y suites de tests. Su objetivo es la cobertura de comportamiento.
3.  **`clean-coder-pro` (Locus: Implementation):** El artesano técnico. Implementa lógica siguiendo arquitectura hexagonal y patrones SOLID, consumiendo las interfaces del architect.
4.  **`formal-validator` (Locus: Quality):** El árbitro de calidad. Valida el cumplimiento estricto del contrato, realiza auditorías de seguridad y asegura el "Zero-Bug Policy".
5.  **`context-memory-manager` (Locus: Persistence):** El gestor de la consciencia. Administra la memoria 4D-TES y el grafo de conocimiento para garantizar la continuidad cognitiva.

## 2. Flujo de Trabajo Riguroso (The MAD Loop 2026)

1.  **Design (`contract-architect`):** Definición formal del contrato de la tarea.
2.  **Verify (`behavior-synth`):** Creación de tests que fallan (Red Phase).
3.  **Execute (`clean-coder-pro`):** Implementación quirúrgica para pasar los tests (Green Phase).
4.  **Audit (`formal-validator`):** Validación cruzada spec-código y auditoría de seguridad.
5.  **Crystallize (`context-memory-manager`):** Registro de la resolución en el grafo de memoria inmutable.

## 3. Directrices de Comunicación
- **Spec-First:** Si no hay spec, no hay tarea.
- **Sovereign Context:** Cada agente debe reportar su estado al `context-memory-manager`.
- **High-Signal Only:** Sin preámbulos. Intención técnica pura.
