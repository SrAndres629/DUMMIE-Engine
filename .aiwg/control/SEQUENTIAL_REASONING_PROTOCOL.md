# SEQUENTIAL_REASONING_PROTOCOL - Misiones Largas

## Propósito
Convertir cada prompt complejo en una misión estructurada con razonamiento externo auditable, evitando la sobrecarga metacognitiva (Context Bloat) y la fragmentación de la sesión.

## Estructura de Sesión Optimizada (.aiwg/sessions/<id>/)
Para evitar el agotamiento de contexto de los LLMs, los 11 artefactos originales se han consolidado en un pipeline funcional de 4 fases que vincula directamente el razonamiento con la ejecución:

1.  **intake_and_plan.md**: (Fase de Ingesta y Estrategia)
    - Reemplaza: `intake.md`, `global_recall.md`, `epistemic_check.md`, `cold_plan.md`, `research_tree.md`.
    - Contiene el diagnóstico del problema, los nodos de memoria relevantes (Contexto 6D) y el plan de acción estructurado antes de codificar.

2.  **execution_trace.md**: (Fase de Ejecución)
    - Reemplaza: `swarm_debate.md`, `patch_plan.md`, `decision_log.md`.
    - Registra exclusivamente las decisiones de diseño tomadas durante la escritura del código y los parches aplicados. Actúa como el mapa funcional del cambio.

3.  **validation_report.md**: (Fase de Verificación)
    - Permanece igual. Contiene la salida bruta de los tests, scripts de auditoría y comandos ejecutados que demuestran empíricamente que la implementación cumple con el `intake_and_plan.md`.

4.  **session_closure.md**: (Fase de Retrospectiva)
    - Reemplaza: `lessons_learned.md`, `next_loop.md`.
    - Breve sumario de heurísticas aprendidas y tareas pendientes que se inyectarán en la siguiente sesión (handoff).

## Clasificación de Evidencia
- **SUPPORTED**: Evidencia física (test ejecutado en verde, código validado).
- **CONTRADICTED**: La realidad del código contradice la especificación. Requiere refactor de spec o de código.
- **ASSUMPTION**: Hipótesis de diseño sin prueba empírica.
- **INSUFFICIENT_EVIDENCE**: El validador L3/L4 no pudo verificar el estado. Requiere iteración adicional.

## Regla de Rigor
El "Cadena de Pensamiento" (CoT) debe ser **funcional, no narrativo**. Todo plan de acción en `intake_and_plan.md` debe poder mapearse unívocamente a líneas de test en `validation_report.md`.
