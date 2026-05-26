# Skill: OpenCode + DUMMIE Engine Native Integration

## Context
OpenCode v1.15.5 es el harness CLI/TUI. DUMMIE Engine es el kernel cognitivo. Su relación es: **DUMMIE gobierna, opencode presenta**. Un plugin TypeScript hookea el ciclo de vida del chat y proporciona herramientas nativas de DUMMIE dentro de opencode.

## SSOT Chain
1. `models_config.json` — modelos disponibles
2. `dummie_gateway_config.json` — topología MCP
3. `meta_router_assignments.json` — tabla de ruteo
4. `scripts/generate_opencode_config.py` → genera `opencode.jsonc`

## Plugin Hooks
| Hook | Función |
|------|---------|
| `tool` | Registra dummie_discover, dummie_route, dummie_swarm |
| `chat.message` | Detecta gateway por sesión |
| `shell.env` | Inyecta DUMMIE_ROOT, modelos, paths |
| `experimental.chat.system.transform` | Inyecta contexto DUMMIE en system prompt |
| `tool.execute.before` | SDD guardrails en tools cloud |
| `experimental.session.compacting` | Preserva gateway assignments |

## Custom Tools
- `dummie_discover(query?)` — descubre capacidades de DUMMIE
- `dummie_route(query)` — rutea un mensaje al sub-gateway correcto
- `dummie_swarm(objective, sessions?)` — coordina swarm multi-sesión

## Models
| Modelo | Rol | Provider |
|--------|-----|----------|
| qwen3-embedding | Routing primario | Ollama |
| gemma4:e2b | LLM default | Ollama |
| gemma4:e4b | LLM deep reasoning | Ollama |
| opencode/deepseek-v4-flash-free | Cloud LLM | OpenRouter |

## Services
```
dummie-memory.service → dummie-engine.service → dummie-opencode.service
                                                     ↓
                                           opencode serve --port 18789
```

## Common Tasks
- **Regenerar config:** `uv run python scripts/generate_opencode_config.py`
- **Verificar routing:** `uv run python -m layers.l1_nervous.meta_router --query "tu mensaje"`
- **Ver plugin activo:** `opencode mcp list` (debe mostrar dummie-brain conectado)
- **Instalar servicios:** `bash scripts/install_services.sh`
