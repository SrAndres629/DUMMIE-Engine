# ADR-0017: LangGraph vs Custom Orchestration Daemon

## 1. Contexto
El DUMMIE Engine ha evolucionado hacia un modelo **Zero-Trust Industrial**. La documentación previa sugería el uso de **LangGraph** como el motor principal de orquestación en la capa L2. Sin embargo, la implementación física actual utiliza un **Custom Async Daemon (Antigravity)** basado en el Patrón Saga, File Locking (fcntl) y validación de DAGs mediante XML y Pydantic.

## 2. Decisión Arquitectónica (Veredicto)
Como Arquitecto Principal, declaro que el **Antigravity Orchestration Daemon** es la **Única Fuente de Verdad (SSoT)** para la orquestación a nivel de sistema (Swarm-Level).

### 2.1. El Nuevo Modelo de Simbiosis:
1. **System Orchestrator (Macro):** El Custom Daemon en `l2_brain/orchestration` gestiona el ciclo de vida del DAG, la resiliencia (Saga), el aislamiento de contexto y la ejecución física (L5 Bridge).
2. **Agent Reasoning (Micro):** **LangGraph** queda relegado a una herramienta opcional de "Razonamiento Interno" para agentes individuales. Un agente puede usar LangGraph para decidir *cómo* realizar una tarea atómica, pero nunca para orquestar a otros agentes o modificar el flujo global del DAG.

## 3. Justificación Técnica
* **Determinismo:** El uso de XML Strict AST y Pydantic en el Custom Daemon garantiza un flujo de control predecible y auditable, vital para aplicaciones B2B industriales.
* **Seguridad Zero-Trust:** Nuestra implementación actual de `sync_cognitive_state` y `exec_remote_tool` está profundamente acoplada al loop asíncrono del Daemon, proporcionando una seguridad que LangGraph (diseñado para fluidez y ciclos) no prioriza por defecto.
* **Soberanía de Memoria:** El Custom Daemon está optimizado para nuestro Ledger persistente y la integración con KùzuDB (4D-TES).

## 4. Impacto
* **Deprecación:** Se eliminan las referencias a LangGraph como "Orquestador del Sistema" en toda la documentación.
* **Alineación:** Todos los agentes futuros deben consumir el Gateway del Custom Daemon para recibir tareas.
