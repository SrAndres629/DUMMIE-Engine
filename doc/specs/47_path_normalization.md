# Spec 47: Path Normalization & Industrial Environment

Para resolver la inconsistencia de rutas detectada ("miles de errores"), se establece el siguiente estándar obligatorio para todos los componentes (L0, L1, L2).

## Variables de Entorno Primarias
- `DUMMIE_ROOT`: Directorio raíz del proyecto (default: `/home/jorand/Escritorio/DUMMIE Engine`).
- `DUMMIE_AIWG`: Directorio de trabajo y memoria (default: `$DUMMIE_ROOT/.aiwg`).

## Mapa de Rutas Estándar
| Recurso | Ruta Estándar | Propósito |
| :--- | :--- | :--- |
| **KùzuDB (Ontología)** | `$DUMMIE_AIWG/memory/kuzu.db` | Memoria a largo plazo (L1). |
| **SQLite (Estado)** | `$DUMMIE_AIWG/memory/state.db` | Persistencia de sesiones flotantes (L0). |
| **Lecciones Learned** | `$DUMMIE_AIWG/memory/lessons.jsonl` | Aprendizaje por refuerzo. |
| **Security State** | `$DUMMIE_AIWG/security_state` | Toggle de bwrap (HIGH/LOW). |
| **Unix Sockets** | `$DUMMIE_AIWG/sockets/` | Comunicación IPC (Flight, Control). |

## Reglas de Implementación
1. **No Hardcoding**: Está terminantemente prohibido usar rutas absolutas literales en el código. Se debe usar `os.Getenv` o `os.environ.get` con fallbacks relativos al root detectado.
2. **Resolución de Root**: Todos los módulos deben intentar detectar el root buscando el archivo `.aiwg` hacia arriba si la variable no está seteada.
3. **Migración**: Se deben actualizar `mcp_proxy.py`, `graph.go`, `store.go` y los scripts de auditoría para usar este esquema.
