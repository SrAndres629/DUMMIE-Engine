# ADR-002: Protocolo de Transporte del SDK

## Estado
Aprobado

## Contexto
El SDK debe transferir grandes grafos de conocimiento (4D-TES) entre el motor y el cliente sin degradar el rendimiento.

## Decisión
Utilizaremos **gRPC** y **Apache Arrow Flight** como el transporte por defecto.
*   Arrow Flight para datos tabulares y grafos (Zero-Copy).
*   gRPC estándar para comandos de control y orquestación.

## Consecuencias
*   **Positivas:** Latencia ultra-baja, comunicación tipada y segura.
*   **Negativas:** Complejidad en el empaquetado del cliente.
