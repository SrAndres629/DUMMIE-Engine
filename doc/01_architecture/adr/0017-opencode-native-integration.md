---
spec_id: DE-ADR-0017
title: OpenCode Native Integration (Cognitive Kernel + Shell Interface)
status: ACCEPTED
version: 1.0.0
layer: L0
namespace: io.dummie.v2.adr
authority: ARCHITECT
dependencies:
- id: DE-ADR-0013
  relationship: EXTENDS
- id: DE-ADR-0015
  relationship: REINFORCES
- id: DE-ADR-0016
  relationship: COMPLEMENTS
tags:
- adr
- opencode
- mcp
- native_integration
- kernel_shell
claims:
- id: 0017-opencode-native-integration-file-valid
  description: Spec file '0017-opencode-native-integration.md' exists, parses valid
    YAML frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/01_architecture/adr/0017-opencode-native-integration.md').read().split('
merged_from:
- adr/ADR-003-Session-State.md
- adr/ADR-004-Opencode-Native-Integration.md
updated: '2026-05-26'
---
')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# ADR-0017: OpenCode Native Integration (Cognitive Kernel + Shell Interface)

## Abstract
OpenCode es el harness CLI/TUI para agentes de IA. DUMMIE Engine es el motor cognitivo que provee routing, modelos, memoria, y sub-gateways por dominio. Esta ADR establece la relación arquitectónica: **DUMMIE como kernel, opencode como shell**. DUMMIE es el SSOT, opencode es la interfaz. Un plugin nativo de opencode hookea el ciclo de vida del chat para rutear cada mensaje a través del MetaGateway de DUMMIE, habilitando multi-chat inteligente por dominio con routing automático y delegación local/cloud.

## Status
**ACCEPTED**

## Context
OpenCode v1.15.5 expone un sistema de plugins con 20+ hooks (chat.params, tool.execute.before/after, experimental.chat.system.transform, shell.env, etc.). DUMMIE Engine tiene un MetaGateway maduro con 5 sub-gateways y 5 estrategias de routing. Sin embargo, la integración actual es superficial — opencode trata a DUMMIE como un MCP server externo cualquiera. Esto causa:

1. **Duplicación de SSOT**: opencode.jsonc y dummie_gateway_config.json pueden divergir.
2. **Routing ignorado**: El MetaGateway de DUMMIE no se usa para decidir qué herramientas/modelos aplicar.
3. **Modelos hardcoded**: opencode usa `opencode/deepseek-v4-flash-free` como modelo, ignorando los modelos locales de DUMMIE (gemma4:e2b, Qwen3-Embedding).
4. **Sin multi-chat por dominio**: Cada sesión de opencode trata todos los dominios igual, sin routing especializado.

## Decision

### 1. DUMMIE como Kernel, OpenCode como Shell
DUMMIE Engine es el SSOT absoluto. OpenCode es una interfaz reemplazable. El flujo es:

```
Usuario → OpenCode CLI/TUI → Plugin DUMMIE → MetaGateway → Sub-Gateway → Herramienta
                                        ↓
                              Router Pipeline (Qwen3-Embedding)
                                        ↓
                              Delegation Engine (local/cloud)
```

### 2. Plugin Nativo de OpenCode
Un plugin TypeScript (`dummie-sdk/plugins/opencode-dummie/`) implementa estos hooks:

| Hook | Función |
|------|---------|
| `chat.params` | Intercepta cada mensaje → lo rutea por MetaGateway de DUMMIE → inyecta dominio + modelo |
| `chat.message` | Log de cada mensaje al ledger de DUMMIE |
| `tool.execute.before` | Inyecta SDD guardrails de DUMMIE antes de ejecutar herramientas |
| `tool.execute.after` | Registra resultado en el evaluador de inteligencia de DUMMIE |
| `shell.env` | Inyecta DUMMIE_ROOT, DUMMIE_AIWG_DIR, rutas de modelos |
| `experimental.chat.system.transform` | Inyecta contexto 6D de DUMMIE en el system prompt |
| `experimental.session.compacting` | Usa memoria 4D-TES para compactación contextual |

### 3. Generación de Config desde SSOT
`scripts/generate_opencode_config.py` lee los SSOTs de DUMMIE y genera `opencode.jsonc`:
- MCP servers desde `dummie_gateway_config.json`
- Modelos desde `models_config.json`
- Plugin config para `dummie-opencode`
- Permissions y timeouts desde especificaciones de DUMMIE

### 4. Multi-Chat Híbrido: Router por Mensaje + Sesiones Paralelas
- **Router por mensaje**: El MetaGateway decide el sub-gateway según el intent del mensaje (media/code/infra/knowledge/shell) usando el pipeline de 5 estrategias.
- **Sesiones paralelas**: Cada sesión de opencode puede tener un contexto de sub-gateway diferente. Swarm de DUMMIE (tools_impl/swarm.py) coordina sesiones paralelas para tareas complejas.

### 5. Modelos
| Rol | Modelo | Provider |
|-----|--------|----------|
| Routing primario | Qwen3-Embedding (0.6B) | Ollama |
| LLM default | gemma4:e2b (5.1B) | Ollama |
| LLM deep | gemma4:e4b (4.5B MoE) | Ollama |
| Cloud LLM | opencode/deepseek-v4-flash-free | OpenRouter |

### 6. systemd
Nuevo servicio `dummie-opencode.service` que arranca opencode con el plugin DUMMIE cargado:
```
[Unit]
Description=OpenCode with DUMMIE Engine native plugin
After=dummie-engine.service dummie-memory.service
Requires=dummie-engine.service
```

## Consecuencias
- **Positivas:** SSOT único para modelos, routing, gateways, y configuración. Multi-chat inteligente sin código hardcoded. Zero deuda técnica (Guardian enforcea). Swarm de sesiones paralelas. OpenCode intercambiable (puede reemplazarse por otro harness).
- **Negativas/Restricciones:** OpenCode requiere DUMMIE Engine corriendo para modo nativo. El plugin TypeScript debe mantenerse sincronizado con la API de opencode (v1.15.5). La generación de config debe ejecutarse cuando cambian los SSOTs de DUMMIE.

---

## [MSA] Sibling Components Requeridos
- **Executable Contract:** `0017-opencode-native-integration.feature`
- **Machine Rules:** `0017-opencode-native-integration.rules.json`
