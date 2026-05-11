# SPEC-71: Meta-Gateway Sensor-First Policy

## Contexto
Para optimizar el consumo de tokens y mejorar la precisión del agente, el descubrimiento de conceptos debe realizarse a través de herramientas sensoriales (Socraticode / Semantic Search / Meta-Gateway) antes de recurrir a la lectura directa de archivos.

## Regla de Oro
**SENSOR-FIRST**: Ningún agente debe leer un archivo completo (`cat`, `view_file`) con propósitos de "descubrimiento de conceptos" sin haber intentado primero una búsqueda semántica o descubrimiento vía Gateway.

## Matriz de Decisión

| Propósito | Condición Previa | Decisión |
|-----------|------------------|----------|
| Concept Discovery | Sin intento de Gateway/Semántico | **WARN / BLOCK** |
| Concept Discovery | Con intento previo | **ALLOW** |
| Line Confirmation | Post-Gateway | **ALLOW** |
| Debug / Stacktrace | Ninguna | **ALLOW** |
| Diff Review | Ninguna | **ALLOW** |

## Implementación
La política se implementa en `layers/l2_brain/metagateway_policy.py` y es consultada por el `DummieDaemon` durante el pre-flight o por los hooks de deliberación.

## Monitoreo
Las violaciones de política se registran en los metadatos de la Saga (`gateway_first_policy: WARN_MODE_ACTIVE`).
