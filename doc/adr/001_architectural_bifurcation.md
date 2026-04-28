# ADR 001: Bifurcación Arquitectónica entre Motores Cognitivos y Sistemas de Negocio

## Status
Proposed

## Context
DUMMIE Engine es un sistema autónomo diseñado para la fabricación de software. Al evaluar el diseño del sistema, se debate si los productos finales (sistemas de negocio) deben compartir la naturaleza adaptativa y autopoyética del motor o si deben ceñirse a paradigmas tradicionales.

## Decision
Se establece una política de separación estricta:
1. **El Constructor (DUMMIE)**: Implementará un núcleo adaptativo y extensible (Gateway Dinámico, Autopoiesis).
2. **Lo Construido (Sistemas de Negocio)**: Implementará Arquitectura Hexagonal (Ports & Adapters), Domain-Driven Design (DDD) y Determinismo Absoluto.

## Consequences
- La generación de código se restringe a patrones predecibles.
- Se prohíbe la mutación autónoma del esquema en sistemas de cliente.
