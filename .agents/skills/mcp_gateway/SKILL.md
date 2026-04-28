---
name: MCP Gateway Dynamic Discovery
description: Protocolo de descubrimiento y ejecución de herramientas delegadas a través del Gateway dummie-brain.
version: 1.0.0
---

# MCP Gateway Pattern

Para evitar la sobrecarga de la ventana de contexto y mantener la interfaz limpia, el DUMMIE Engine utiliza un **Gateway Pattern** para acceder a herramientas. Como agente LLM, no tendrás todas las herramientas cargadas directamente en tu `mcp.json`. En su lugar, usarás `dummie-brain` como tu único hub.

## Flujo de Trabajo Cognitivo (Workflow)

Cuando necesites utilizar capacidades que no tienes de forma nativa (por ejemplo, buscar en Github, usar Git, consultar una Base de Datos SQLite, leer Puppeteer, etc.), **debes usar el Gateway** siguiendo este proceso:

### 1. Descubrir Servidores
Si no estás seguro de qué servidor utilizar, usa la herramienta para ver los servidores proxyados.
**Herramienta:** `mcp_dummie-brain_list_remote_servers`

### 2. Descubrir Herramientas
Una vez que sepas el nombre del servidor (ej. `git`), consulta qué herramientas tiene disponibles y qué parámetros necesitan.
**Herramienta:** `mcp_dummie-brain_list_remote_tools(server_name="git")`
Esto te devolverá la lista de herramientas, como `git_status`, `git_commit`, etc.

### 3. Ejecutar la Herramienta
Usa la herramienta genérica de ejecución para invocar la herramienta remota, pasando los argumentos como un objeto JSON (diccionario).
**Herramienta:** `mcp_dummie-brain_exec_remote_tool`
- `server_name`: "git"
- `tool_name`: "git_status"
- `arguments`: {} (Cualquier argumento requerido, si aplica)

---

## ⚠️ Reglas Estrictas de Ejecución
1. **Evita la asunción de argumentos:** Si no estás 100% seguro de los parámetros de una herramienta remota, ejecuta `list_remote_tools` primero.
2. **Usa el Gateway sobre comandos directos:** Si existe un MCP server para la tarea (ej. Git, Fetch, SQLite), prioriza usar `exec_remote_tool` sobre comandos de terminal a menos que el servidor MCP falle.
3. **Manejo de Errores:** Si `exec_remote_tool` devuelve un `SDD_BLOCKED`, significa que la política Zero-Trust (SDD Guardrails) ha bloqueado tu acción. Debes revisar tu plan arquitectónico antes de insistir.

## Ejemplos de Servidores Frecuentes
- `git`: Control de versiones.
- `sqlite`: Bases de datos relacionales locales.
- `filesystem`: Lectura/escritura (aunque posees herramientas nativas).
- `fetch`: Lectura de páginas web y URLs.
- `ripgrep`: Búsquedas de alto rendimiento.
