# METODOLOGÍA MULTI-AGENTE DUMMIE (MAD)

Este proyecto utiliza una metodología de trabajo multi-agente rigurosa basada en la especialización por "Locus" (áreas de responsabilidad).

## 1. El Equipo de Agentes
El desarrollo se delega en 5 agentes especializados accesibles vía `invoke_agent`:

1.  **`investigator` (Locus: Research):** Audita el código, analiza requerimientos y mapea dependencias. **Es el primer paso de cualquier tarea.**
2.  **`architect-fixer` (Locus: Implementation):** El brazo ejecutor. Crea código limpio, testeado y sigue la arquitectura hexagonal.
3.  **`scribe` (Locus: Memory):** Documenta lecciones, ADRs y READMEs. Evita la pérdida de conocimiento sistémico.
4.  **`overseer-meta` (Locus: Control):** Monitorea la eficiencia, el plan estratégico y realiza auditorías de razonamiento.
5.  **`tool-augmentor` (Locus: Infrastructure):** **NUEVO.** Descubre nuevas herramientas MCP en internet, crea skills y optimiza el flujo técnico del equipo.

## 2. Flujo de Trabajo Riguroso (The MAD Loop)
Toda tarea de software debe seguir este ciclo:

1.  **Investigación (`investigator`):** Recopilación de hechos y validación de suposiciones.
2.  **Estrategia (`overseer-meta` + `mcp_sequentialthinking`):** Diseño del plan de ataque y verificación de viabilidad.
3.  **Aumentación (Opcional - `tool-augmentor`):** Si la tarea requiere herramientas que no tenemos, este agente las busca o crea.
4.  **Ejecución (`architect-fixer`):** Implementación técnica, tests y validación física.
5.  **Crystallization (`scribe`):** Documentación del resultado y lecciones aprendidas.

## 3. Directrices de Comunicación
- **High-Signal Only:** Evitar preámbulos. Ir directamente a la intención técnica y el rationale arquitectónico.
- **Delegación Inteligente:** No intentes hacerlo todo tú solo. Si una sub-tarea es compleja o requiere mucha investigación, delégala al agente correspondiente.
- **Validación Mandatoria:** Nada se considera terminado sin pruebas de éxito.
