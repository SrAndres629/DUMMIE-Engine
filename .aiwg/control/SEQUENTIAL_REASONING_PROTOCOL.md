# SEQUENTIAL_REASONING_PROTOCOL - Misiones Largas

## Propósito
Convertir cada prompt complejo en una misión estructurada con razonamiento externo auditable, evitando la pérdida de contexto en sesiones largas.

## Estructura de Sesión (.aiwg/sessions/<id>/)
Toda misión debe generar los siguientes artefactos:

1.  **intake.md**: Análisis de requerimientos y objetivos.
2.  **global_recall.md**: Recuperación de memoria del repo (File Cards, Contexto 6D).
3.  **epistemic_check.md**: Validación de premisas y búsqueda de contradicciones.
4.  **cold_plan.md**: Plan de acción detallado antes de editar.
5.  **research_tree.md**: Árbol de exploración de soluciones.
6.  **swarm_debate.md**: Debate externo entre roles con handoff verificable.
7.  **patch_plan.md**: Dif detallado de cambios.
8.  **validation_report.md**: Evidencia de tests y auditoría.
9.  **decision_log.md**: Justificación de decisiones tomadas.
10. **lessons_learned.md**: Patrones detectados para el futuro.
11. **next_loop.md**: Pendientes para la siguiente sesión.

## Clasificación de Evidencia
- **SUPPORTED**: Evidencia física (test, código).
- **CONTRADICTED**: La realidad contradice la spec.
- **ASSUMPTION**: Hipótesis sin validar.
- **INSUFFICIENT_EVIDENCE**: Se requiere más investigación.
