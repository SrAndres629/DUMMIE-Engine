# Engineering Principles: Evolvability & Structural Integrity

Este documento establece los principios técnicos mandatorios para cualquier intervención en el DUMMIE Engine. El objetivo es garantizar que el sistema sea evolutivo, mantenible y resistente a regresiones.

## 1. Evolvability First
Un arreglo no está completo si solo hace que el síntoma desaparezca. Debe reducir la probabilidad de que el mismo tipo de problema regrese.

## 2. Contratos Estables y Centralizados
- **Single Source of Truth (SSoT):** Esquemas (Zod, Pydantic, Protobuf), rutas, configuraciones y protocolos deben tener una única definición canónica.
- **Sin Duplicación:** No dupliques lógica de rutas o esquemas entre capas (L1, L2, Scripts).
- **Rutas Canónicas:** Utiliza variables de entorno o políticas de resolución centralizadas (ej. `loci.db`) en lugar de rutas absolutas hardcodeadas.

## 3. Fallos Explícitos (No Silent Failures)
- No silencies errores que afecten la persistencia, memoria, orquestación o seguridad.
- Si una operación de escritura en memoria falla y es requerida, el sistema debe lanzar una excepción o entrar en un estado de error observable.

## 4. Integridad de Datos y Persistencia
- **No Destructivo:** Nunca borres o recrees almacenes de datos persistentes sin backup, migración y verificación explícita.
- **Compatibilidad:** Preserva la compatibilidad hacia atrás a menos que exista un plan de migración y tests que demuestren que la ruptura es intencional.

## 5. Pruebas Antirregresión
- Cada corrección de bug debe incluir o actualizar un test de regresión que fallaría si el bug regresa.
- Cada cambio arquitectónico debe incluir comandos de verificación y evidencia de éxito.

## 7. Inteligencia Semántica (Embeddings)
- **Single Source of Meaning:** Entidades críticas (Herramientas, Memorias) deben poseer un vector de embedding denso (384 dim).
- **Lazy Load:** Los modelos de ML deben cargarse perezosamente para no penalizar el arranque.
- **Similitud Causal:** El sistema debe usar similitud vectorial para recuperar conocimientos y capacidades de forma asociativa.
