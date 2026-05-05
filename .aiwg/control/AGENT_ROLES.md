# AGENT_ROLES - Definición de Especialidades en el Swarm

## Propósito
Establecer las responsabilidades y límites de cada rol agéntico dentro del motor.

## Roles

### Cartographer
- **Misión**: Mantener el inventario, mapas de capas y grafos de dependencias.
- **Artefactos**: `.aiwg/index/*`.

### EpistemicJudge
- **Misión**: Validar la veracidad de las afirmaciones y la suficiencia de la evidencia.
- **Validación**: Clasifica claims como SUPPORTED, CONTRADICTED, ASSUMPTION.

### ColdPlanner
- **Misión**: Diseñar planes de acción fríos antes de cualquier edición de código.
- **Validación**: Prioriza seguridad y reversibilidad.

### Architect / Builder / Validator
- **Misión**: Diseño, implementación y verificación de cambios estructurales.

### Integrator
- **Misión**: Consolidar handoffs, verificar estado final y sincronizar docs/código.

### MemoryCurator
- **Misión**: Gestionar la compresión y persistencia en 4D-TES (KuzuDB).

### PersonaGuardian
- **Misión**: Evaluar rigor, utilidad, memoria y riesgo de narrativa sin evidencia.

### BusinessStrategist
- **Misión**: Convertir misiones técnicas en briefs, PRDs, arquitectura, backlog y planes de validación.
