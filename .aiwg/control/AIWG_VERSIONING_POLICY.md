# AIWG Versioning Policy

## Propósito
Separar de forma estricta la memoria dinámica (estado, sesiones, índices temporales) de los protocolos inmutables o versionables de DUMMIE Engine, para evitar ensuciar el repositorio principal.

## Política Git

### Commit to Git (Versionables)
Estas carpetas contienen reglas de comportamiento y deben versionarse:
- `.aiwg/README.md`
- `.aiwg/control/`
- `.aiwg/templates/`
- `.aiwg/self_model/`
- `.aiwg/identity.json`
- `.aiwg/ontological_map.json`
- `.aiwg/obsidian_vault/` configuracion, notas y plugins seguros

### Local Only (No versionables)
Estas carpetas contienen memoria dinámica generada en ejecución y NO deben versionarse:
- `.aiwg/index/`
- `.aiwg/events/`
- `.aiwg/sessions/`
- `.aiwg/cache/`
- `.aiwg/runtime/`
- `.aiwg/memory/`
- `.aiwg/ledger/`
- `.aiwg/security_state`
- `.aiwg/venv_ssh/`
- `.aiwg/*.jsonl`
- `.aiwg/*.db`
- `.aiwg/obsidian_vault/**/.obsidian/plugins/*/data.json` porque contiene credenciales locales del plugin

### Workspaces Locales
`.aiwg/workspaces/` no se excluye de la lectura de agentes, pero sus repositorios anidados no se versionan automaticamente en el monorepo principal. Si un workspace debe conservarse, debe promoverse mediante una politica explicita de submodulo, worktree externo o snapshot curado.
