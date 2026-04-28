# MANIFIESTO DE ORQUESTACIÓN DE ENJAMBRES AUTÓNOMOS Y PERSISTENCIA COGNITIVA
## DUMMIE Engine Core Specification — Edición 2026

### 1. VISIÓN Y PROPÓSITO FUNDAMENTAL
El ecosistema DUMMIE Engine está diseñado para la **ejecución asíncrona prolongada y supervisada de múltiples agentes inteligentes.** El objetivo final es el despliegue de un entorno donde los agentes operen metódicamente durante horas o días, manteniendo al humano constantemente informado y en control (Human-in-the-Loop) mediante interfaces ubicuas (ej: mensajería supervisada vía WhatsApp).

### 2. GOBERNANZA DE ENJAMBRES HETEROGÉNEOS (Multi-Model Swarms)
Reconocemos que el futuro de la inteligencia artificial no reside en un único modelo cerrado, sino en enjambres distribuidos de diferentes proveedores y tamaños. 
*   **Abstracción vía Gateway MCP**: El sistema nervioso desacopla las capacidades del proveedor del modelo. El uso del Gateway y el motor 4D-TES debe estar **completamente libre de excepciones no controladas**.
*   **Homogeneización del Estado**: Los modelos de diferentes compañías operarán bajo el mismo protocolo unificado de intercambio de datos (Zero-Copy/Apache Arrow), garantizando interoperabilidad estricta.

### 3. PERSISTENCIA GEODÉSICA: EL MOTOR 4D-TES
Rechazamos el almacenamiento volátil y los historiales de chat lineales. 
*   **Consolidación del Contexto**: A través de KùzuDB y grafos causales deterministas, los agentes guardan el estado lógico y las intenciones pausadas. 
*   Si la conexión física se interrumpe o un agente "duerme" esperando supervisión humana, la reanudación no requiere reprocesar miles de tokens redundantes. La IA retoma el hilo cognitivo extrayendo las coordenadas geométricas exactas de su última acción exitosa.

### 4. MANDATO DE INGENIERÍA: SPECS-DRIVEN DEVELOPMENT (SDD)
Prohibimos soluciones rápidas, parches locales y código "frágil" que obligue a los agentes a estar corrigiendo rutas o adaptando configuraciones en cada iteración.
*   **Single Source of Truth (SSoS)**: Ningún agente escribirá código sin un contrato tipado previo (Zod/Pydantic/JSON Schema).
*   **Inversión de Dependencias (DIP)**: El dominio puro de negocio se mantendrá aislado de la infraestructura MCP. Las refactorizaciones futuras no romperán el núcleo del sistema.

### 5. COMPROMISO DE ESCALABILIDAD
El orquestador debe operar con un consumo optimizado y seguro de recursos. Cada línea de código generada por el enjambre será mantenible y tolerante a fallos, priorizando la arquitectura limpia para asegurar que el software evolucione orgánicamente sin degradación técnica.
