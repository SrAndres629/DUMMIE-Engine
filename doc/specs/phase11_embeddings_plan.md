# Phase 11: Semantic Embedding & Context Compression

## Objetivo
Reemplazar los fallbacks basados en hashes crudos y heurísticas simples por un motor semántico formal basado en Pydantic y Protocolos. Esto habilitará que el sistema pueda buscar en la memoria por "significado" (Embedding) y recortar el contexto inteligentemente según el "presupuesto de tokens" (Compression).

## 10 Micro-Fases de Implementación (Spec-Driven)

### Bloque 1: Contratos y Schemas (SDD)
- **1. Schemas de Embedding:** Definir `EmbeddingRequest` y `EmbeddingResponse` usando Pydantic en `embedding_contract.py`.
- **2. Schemas de Compresión:** Definir `CompressionRequest` y `CompressionResponse` (para el token budget) en `compression_contract.py`.
- **3. TDD de Contratos:** Escribir `test_embedding_contracts.py` asegurando la validación estricta de tipos.

### Bloque 2: Adaptadores Semánticos (Hexagonal Ports)
- **4. Puerto IEmbeddingAdapter:** Crear la interfaz base para aislar la librería física.
- **5. Adaptador FastEmbed:** Implementar la clase física `FastEmbedAdapter` (para no depender de APIs externas como OpenAI y usar la CPU/GPU local).
- **6. TDD de FastEmbed:** Probar que el adaptador realmente convierte texto en vectores float.

### Bloque 3: Compresor de Contexto (Context Shaper)
- **7. Protocolo ContextCompressor:** Crear la interfaz para el compresor de contexto.
- **8. Implementación LocalContextCompressor:** Escribir la lógica que ordena snippets por relevancia semántica y recorta (truncate) si excede los tokens.
- **9. TDD del Compresor:** Probar la lógica de truncamiento exacto de tokens (simulando 4000 tokens limit).

### Bloque 4: Integración (The Brain)
- **10. Conexión L2:** Inyectar el `EmbeddingAdapter` y el `LocalContextCompressor` dentro del `CognitiveOrchestrator` o `VaultContextResolver` para habilitar el uso real en las consultas MCP.
