import os
import logging
import sys

# [ANTIGRAVITY] Purity Guard: Evitar contaminación de stdout durante el bootstrap
_actual_stdout = sys.stdout
sys.stdout = sys.stderr

from mcp.server.fastmcp import FastMCP

# [TABULA RASA v2] Importaciones Planas
from bootstrap import bootstrap_orchestrator, setup_shutdown_handlers
from tools import register_tools
from resources import register_resources
from mcp_proxy import MCPProxyManager

# Configuración (SSoT)
ROOT_DIR = os.environ.get("DUMMIE_ROOT_DIR", "/home/jorand/Escritorio/DUMMIE Engine")
AIWG_DIR = os.environ.get("DUMMIE_AIWG_DIR", os.path.join(ROOT_DIR, ".aiwg"))
KUZU_DB_PATH = os.environ.get("DUMMIE_KUZU_DB_PATH", os.path.join(AIWG_DIR, "memory/loci.db"))

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
    mcp.run()
