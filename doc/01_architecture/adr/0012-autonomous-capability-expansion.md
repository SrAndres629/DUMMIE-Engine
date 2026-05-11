---
spec_id: "DE-V2-L0-ADR-0012"
title: "Expansión Autónoma de Capacidades (MCP y Skills)"
status: "ACCEPTED"
version: "1.0.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
---

# ADR-0012: Expansión Autónoma de Capacidades (MCP y Skills)

## Contexto y Problema
El enjambre de agentes del DUMMIE Engine depende de sus periferias cognitivas (MCPs) y habilidades procedimentales (Skills) para interactuar con el mundo físico y realizar tareas de alta complejidad. Actualmente, la adición de estas capacidades es reactiva o manual, lo que limita la evolución soberana del sistema ante nuevos desafíos técnicos o ineficiencias detectadas (ej. consumo excesivo de tokens, falta de herramientas de análisis estructural).

Para alcanzar la madurez como una *Software Fabrication Engine* (SFE) verdaderamente autónoma, el sistema debe ser capaz de identificar sus propias limitaciones y proponer o ejecutar la instalación de nuevas "prótesis cognitivas".

## Decisión Arquitectónica
Se establece el mandato de que el enjambre de agentes (específicamente `sw.strategy.discovery` y `sw.arch.core`) tiene la autoridad y la responsabilidad de:
1.  **Búsqueda Proactiva:** Consultar registros de MCP (como el MCP Registry oficial) y repositorios de habilidades al detectar una brecha de eficiencia.
2.  **Creación de Skills:** Desarrollar autónomamente nuevos scripts o módulos de lógica (`L2 Skills`) cuando no exista una herramienta externa adecuada.
3.  **Instalación y Configuración:** Modificar los archivos de configuración (`mcp_config.json`, `settings.json`) para integrar nuevas herramientas, priorizando instalaciones locales y ligeras (vía `uvx`, `cargo` o binarios estáticos en unidades de datos).
4.  **Optimización de Contexto:** Buscar e integrar herramientas que reduzcan el "ruido" en el prompt (como analizadores de esqueletos de código o diffs inteligentes) para maximizar la parsimonia de tokens.

## Consecuencias
- **Positivas:**
    - **Evolución Soberana:** El sistema reduce su dependencia de la intervención humana para optimizar su propio flujo de trabajo.
    - **Eficiencia Operativa:** Reducción drástica en el consumo de tokens y mejora en la precisión de las ediciones de código.
    - **Escalabilidad:** Capacidad de adaptarse a cualquier stack tecnológico mediante la adquisición bajo demanda de nuevas herramientas.
- **Negativas/Restricciones:**
    - **Riesgo de Seguridad:** La instalación autónoma debe ser validada contra políticas de seguridad (Shields) para evitar la ejecución de código malicioso.
    - **Gestión de Dependencias:** El sistema debe ser capaz de limpiar herramientas obsoletas o redundantes para evitar el "bloatware" cognitivo.

---

## [MSA] Sibling Components Requeridos
Todo ADR debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** `0012-autonomous-capability-expansion.feature`
- **Machine Rules:** `0012-autonomous-capability-expansion.rules.json`
