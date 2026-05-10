# REASONING_PROTOCOL - Razonamiento Secuencial Externo

## Propósito
Asegurar que el proceso de pensamiento sea transparente, auditable y persistente fuera del contexto volátil del LLM.

## Formato
Todo razonamiento complejo debe producir artefactos en `.aiwg/sessions/<session_id>/`:
1. `intake.md`: Análisis de la solicitud.
2. `epistemic_check.md`: Validación de premisas.
3. `cold_plan.md`: Estrategia de ejecución.
4. `decision_log.md`: Registro de elecciones y rechazos.

## Reglas de Oro
- No ocultar la "Cadena de Pensamiento" si afecta la integridad del código.
- Clasificar cada paso: [INVESTIGACIÓN], [PLAN], [ACTO], [VALIDACIÓN].
