---
status: APPROVED
layer: adr
domain: [opencode, integration, native]
---
# ADR-004: Integración Nativa OpenCode + DUMMIE Engine

## Estado
Aprobado

## Contexto
OpenCode (v1.15.5) es el harness CLI/TUI actual para agentes de IA, con sistema de plugins, hooks, y soporte MCP nativo. DUMMIE Engine tiene un MetaGateway con 5 sub-gateways (media/code/infra/knowledge/shell), routing pipeline de 5 estrategias (ExactMatch → EmbeddingMatch con Qwen3-Embedding → CrossEncoderRerank → CoT → LLM), delegación local/cloud, y sistema de memoria 4D-TES con Kuzu.

Actualmente opencode ve a DUMMIE como un MCP server externo cualquiera (`dummie-brain`). No hay conciencia de DUMMIE como plataforma — no usa el MetaGateway, no usa el routing pipeline, no usa el SDK. Esto duplica lógica de ruteo, fragmenta la configuración de modelos, e impide el multi-chat inteligente por dominio.

## Decisión
DUMMIE Engine será el **kernel cognitivo** y opencode será el **shell de interfaz**. La relación es: DUMMIE gobierna, opencode presenta. Esto se materializa en:

1. **SSOT único DUMMIE**: `models_config.json`, `dummie_gateway_config.json`, `meta_router_assignments.json` son la única fuente de verdad. `opencode.jsonc` se genera automáticamente desde DUMMIE vía `generate_opencode_config.py`.

2. **Plugin nativo de opencode**: Un plugin TypeScript (`plugins/opencode-dummie/`) que hookea `chat.params` para rutear mensajes a través del MetaGateway de DUMMIE, inyecta SDD guardrails via `tool.execute.before`, y proporciona contexto DUMMIE via `experimental.chat.system.transform`.

3. **Sistema híbrido router + multi-sesión**: Cada mensaje se rutea al sub-gateway correcto (media/code/infra/knowledge/shell) según el intent. Cada sesión de opencode puede tener su propio router y contexto aislado. Swarm de DUMMIE coordina sesiones paralelas.

4. **Qwen3-Embedding como modelo primario de routing**: Reemplaza `BAAI/bge-small-en-v1.5` como embedding por defecto. 0.6B parámetros, SOTA en MTEB para clasificación y routing de intenciones.

5. **systemd dummie-opencode.service**: Servicio systemd que arranca opencode con el plugin DUMMIE cargado, dependiente de `dummie-engine.service`.

## Consecuencias
- **Positivas:** Un solo SSOT para modelos, routing, y gateways. Multi-chat inteligente por dominio. Zero hardcoded model strings (enforced por Guardian). Swarm de sesiones paralelas. OpenCode como interfaz reemplazable (puede intercambiarse por otro harness sin perder capacidades).
- **Negativas/Restricciones:** Requiere que DUMMIE Engine esté corriendo (systemd) para que opencode funcione en modo nativo. El plugin TypeScript debe mantenerse sincronizado con la API de opencode.
