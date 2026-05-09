# ADR-001: Arquitectura del SDK de DUMMIE Engine

## Estado
Aprobado

## Contexto
Necesitamos una interfaz programática para que los desarrolladores interactúen con las capacidades L0-L6 del motor de manera idiomática.

## Decisión
Construiremos el SDK primario en **Python** utilizando un diseño orientado a objetos limpio, soportando:
*   Inicialización fluida (`dummie.Client()`).
*   Context Managers para sesiones de agentes.
*   Integración nativa con Pydantic.

## Consecuencias
*   **Positivas:** Alta compatibilidad con el ecosistema de IA actual.
*   **Negativas:** Para soportar frontend (JS), se requerirá un proxy HTTP intermedio.
