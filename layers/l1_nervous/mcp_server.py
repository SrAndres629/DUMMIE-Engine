import os
import logging
import sys

# [TABULA RASA v2] SSoT de Rutas (Prioridad Máxima)
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
ROOT_DIR = os.environ.get("DUMMIE_ROOT", os.environ.get("DUMMIE_ROOT_DIR", _DEFAULT_ROOT))

# [TECHNICAL DEBT] sys.path manipulation
# WHY: L1 imports modules from L2 and L3 via flat namespace (e.g. `from models import ...`).
# The correct fix is proper Python packaging with pyproject.toml or namespace packages.
# This hack adds each layer directory to sys.path so flat imports resolve.
# SCOPE: Exactly 3 paths added (l1_nervous, l2_brain, l3_shield).
# RISK: Import collisions between layers with same-named modules.
# TRACKED: autorefactor_state.yaml -> sys_path_hacks_removed = false
for _layer in ["l1_nervous", "l2_brain", "l3_shield"]:
    _layer_path = os.path.join(ROOT_DIR, "layers", _layer)
    if os.path.exists(_layer_path) and _layer_path not in sys.path:
        sys.path.insert(0, _layer_path)

from mcp.server.fastmcp import FastMCP

# Importaciones locales (ahora seguras)
from bootstrap import bootstrap_orchestrator, setup_shutdown_handlers
from tools import register_tools
from resources import register_resources
from mcp_proxy import MCPProxyManager

# Configuración (Resto)
AIWG_DIR = os.environ.get("DUMMIE_AIWG", os.environ.get("DUMMIE_AIWG_DIR", os.path.join(ROOT_DIR, ".aiwg")))
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

# Bootstrap perezoso para estabilidad multi-CLI
_orchestrator = None
_proxy_manager = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = bootstrap_orchestrator(KUZU_DB_PATH, AIWG_DIR)
    return _orchestrator

def get_proxy():
    global _proxy_manager
    if _proxy_manager is None:
        _proxy_manager = MCPProxyManager(MCP_CONFIG_PATH)
    return _proxy_manager

# Registro dinámico
register_tools(mcp, get_orchestrator, get_proxy, ROOT_DIR)
register_resources(mcp, get_orchestrator, get_proxy, ROOT_DIR)

if __name__ == "__main__":
    # [TECHNICAL DEBT] STDIO Purity Guard
    # WHY: FastMCP STDIO transport requires exclusive control of stdout.
    # Any print() or logging to stdout during bootstrap corrupts the MCP protocol.
    # The correct fix requires FastMCP to support a file descriptor override,
    # or running the server in a subprocess with controlled file descriptors.
    # SCOPE: stdout is redirected to stderr ONLY within this __main__ block.
    _actual_stdout = sys.stdout
    sys.stdout = sys.stderr

    logger.info("DUMMIE Brain Gateway (FLAT-L1) Online.")
    sys.stdout = _actual_stdout
    
    try:
        # Forzar el transporte STDIO de forma explícita y segura
        mcp.run(transport='stdio')
    except Exception as e:
        logger.critical(f"Gateway Crash: {e}", file=sys.stderr)
    finally:
        # Garantizar limpieza de procesos huérfanos al cerrarse el pipe STDIO
        import asyncio
        if _proxy_manager:
            try:
                # Usar un timeout para no bloquear el cierre
                asyncio.run(asyncio.wait_for(_proxy_manager.shutdown(), timeout=2.0))
            except Exception:
                pass

