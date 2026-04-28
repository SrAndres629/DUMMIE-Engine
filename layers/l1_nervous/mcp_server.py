import os
import logging
import sys

# [ANTIGRAVITY] Purity Guard: Evitar contaminación de stdout durante el bootstrap
_actual_stdout = sys.stdout
sys.stdout = sys.stderr

# [TABULA RASA v2] SSoT de Rutas (Prioridad Máxima)
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
ROOT_DIR = os.environ.get("DUMMIE_ROOT", os.environ.get("DUMMIE_ROOT_DIR", _DEFAULT_ROOT))

# Asegurar que todas las capas estén en PYTHONPATH
for layer in ["l1_nervous", "l2_brain", "l3_shield"]:
    layer_path = os.path.join(ROOT_DIR, "layers", layer)
    if os.path.exists(layer_path) and layer_path not in sys.path:
        sys.path.insert(0, layer_path)

from mcp.server.fastmcp import FastMCP

# Importaciones locales (ahora seguras)
from bootstrap import bootstrap_orchestrator, setup_shutdown_handlers
from tools import register_tools
from resources import register_resources
from mcp_proxy import MCPProxyManager

# Configuración (Resto)
AIWG_DIR = os.environ.get("DUMMIE_AIWG", os.environ.get("DUMMIE_AIWG_DIR", os.path.join(ROOT_DIR, ".aiwg")))
KUZU_DB_PATH = os.environ.get("DUMMIE_KUZU_DB_PATH", os.path.join(AIWG_DIR, "memory/kuzu.db"))

_EXPLICIT_MCP_CONFIG_PATH = os.environ.get("DUMMIE_MCP_CONFIG_PATH")
_DEFAULT_REGISTRY_PATH = os.path.expanduser("~/.gemini/antigravity/mcp_config.registry.json")

if _EXPLICIT_MCP_CONFIG_PATH:
    MCP_CONFIG_PATH = _EXPLICIT_MCP_CONFIG_PATH
else:
    _candidates = [
        _DEFAULT_REGISTRY_PATH,
        os.path.join(ROOT_DIR, "dummie_agent_config.json"),
        os.path.join(AIWG_DIR, "mcp_config.registry.json"),
    ]
    MCP_CONFIG_PATH = next((p for p in _candidates if os.path.exists(p)), _DEFAULT_REGISTRY_PATH)

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("dummie-mcp.main")

mcp = FastMCP("DUMMIE-Brain-Gateway")

# Bootstrap
orchestrator = bootstrap_orchestrator(KUZU_DB_PATH, AIWG_DIR)
proxy_manager = MCPProxyManager(MCP_CONFIG_PATH)

setup_shutdown_handlers(orchestrator, proxy_manager)

# Registro
register_tools(mcp, orchestrator, proxy_manager, ROOT_DIR)
register_resources(mcp, orchestrator, proxy_manager, ROOT_DIR)

if __name__ == "__main__":
    logger.info("DUMMIE Brain Gateway (FLAT-L1) Online.")
    # Restaurar stdout para el servidor MCP
    sys.stdout = _actual_stdout
    try:
        mcp.run()
    except KeyboardInterrupt:
        pass
    finally:
        # Garantizar limpieza de procesos huérfanos al cerrarse el pipe STDIO
        import asyncio
        try:
            asyncio.run(proxy_manager.shutdown())
        except Exception:
            pass
