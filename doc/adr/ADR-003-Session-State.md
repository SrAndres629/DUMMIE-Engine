# ADR-003: Gestión de Estado y Sesiones

## Estado
Aprobado

## Contexto
Los agentes multi-turno necesitan reanudar contextos pasados sin perder coherencia causal.

## Decisión
El SDK no almacenará estado local. Actuará como un cliente delgado (**Thin Client**). 
*   Toda sesión generará un `session_id` mapeado en el 4D-TES.
*   El SDK enviará comandos referenciando este ID.

## Consecuencias
*   **Positivas:** Tolerancia a caídas del cliente; consistencia total.
*   **Negativas:** Requiere conexión persistente para streaming de logs.
