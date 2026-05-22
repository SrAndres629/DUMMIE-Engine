import os
import logging
import sys

# [TABULA RASA v2] SSoT de Rutas (Prioridad Máxima)
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
ROOT_DIR = os.environ.get(
    "DUMMIE_ROOT", os.environ.get("DUMMIE_ROOT_DIR", _DEFAULT_ROOT)
)

# [TECHNICAL DEBT] sys.path manipulation
# WHY: L1 imports modules from L2 and L3 via flat namespace (e.g. `from models import ...`).
# Also, many L2 modules use absolute imports (e.g. `from layers.l2_brain...`).
# MITIGATION: Consolidated routing using ROOT_DIR and canonical layer offsets.
# Import collisions are prevented by path uniqueness checks.
# TRACKED: reports/autorefactor_state.yaml -> sys_path_hacks_removed = false (mitigated/verified)

_paths_to_insert = [ROOT_DIR]
for _layer in ["l1_nervous", "l2_brain", "l3_shield"]:
    _paths_to_insert.append(os.path.join(ROOT_DIR, "layers", _layer))
_paths_to_insert.append(os.path.join(ROOT_DIR, "layers", "l2_brain", "src"))

for _path in _paths_to_insert:
    _abs_path = os.path.abspath(_path)
    if os.path.exists(_abs_path) and _abs_path not in sys.path:
        sys.path.insert(0, _abs_path)


# [HARDENING] STDIO Purity Guard (Global Monkeypatch)
# WHY: Any print() to stdout from any imported module will corrupt the MCP protocol.
import builtins

_orig_print = builtins.print


def guarded_print(*args, **kwargs):
    if kwargs.get("file") is None or kwargs.get("file") == sys.stdout:
        kwargs["file"] = sys.stderr
    _orig_print(*args, **kwargs)


builtins.print = guarded_print

from mcp.server.fastmcp import FastMCP

# Importaciones locales (ahora seguras)
from layers.l1_nervous.bootstrap import bootstrap_orchestrator, setup_shutdown_handlers
from layers.l1_nervous.tools import register_tools
from layers.l1_nervous.resources import register_resources
from layers.l1_nervous.mcp_proxy import MCPProxyManager

# Configuración (Resto)
AIWG_DIR = os.environ.get(
    "DUMMIE_AIWG", os.environ.get("DUMMIE_AIWG_DIR", os.path.join(ROOT_DIR, ".aiwg"))
)
KUZU_DB_PATH = os.environ.get(
    "DUMMIE_KUZU_DB_PATH", os.path.join(AIWG_DIR, "memory/loci.db")
)

_EXPLICIT_MCP_CONFIG_PATH = os.environ.get("DUMMIE_MCP_CONFIG_PATH")
_DEFAULT_REGISTRY_PATH = os.path.expanduser("~/.antigravity/mcp_config.registry.json")

if _EXPLICIT_MCP_CONFIG_PATH:
    MCP_CONFIG_PATH = _EXPLICIT_MCP_CONFIG_PATH
else:
    _candidates = [
        _DEFAULT_REGISTRY_PATH,
        os.path.join(ROOT_DIR, "dummie_gateway_config.json"),
        os.path.join(ROOT_DIR, "dummie_agent_config.json"),
        os.path.join(AIWG_DIR, "mcp_config.registry.json"),
    ]
    MCP_CONFIG_PATH = next(
        (p for p in _candidates if os.path.exists(p)), _DEFAULT_REGISTRY_PATH
    )

# [HARDENING] Silence all stdout logging
logging.basicConfig(level=logging.WARNING, stream=sys.stderr, force=True)
logger = logging.getLogger("dummie-mcp.main")
logger.setLevel(logging.WARNING)

mcp = FastMCP("DUMMIE-Brain-Gateway")

# Watchdog: archivo de readiness para orquestadores externos
_READINESS_FILE = os.path.join(AIWG_DIR, "state", "mcp_gateway.ready")
_WATCHDOG_INTERVAL = 30  # segundos entre health checks


def _write_readiness(ready: bool | str):
    try:
        os.makedirs(os.path.dirname(_READINESS_FILE), exist_ok=True)
        with open(_READINESS_FILE, "w") as f:
            if isinstance(ready, bool):
                f.write("ready" if ready else "degraded")
            else:
                f.write(ready)
    except Exception:
        pass


def _log_quarantine(status: str, detail: str):
    try:
        qdir = os.path.join(AIWG_DIR, "runtime", "quarantine")
        os.makedirs(qdir, exist_ok=True)
        ts = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(os.path.join(qdir, f"gateway_crash_{ts}.log"), "w") as f:
            f.write(f"STATUS: {status}\nDETAIL: {detail}\n")
    except Exception:
        pass


def _validate_db_path(db_path: str) -> bool:
    if not db_path:
        logger.warning("KUZU_DB_PATH vacío, orquestador en modo degradado")
        return False
    if not os.path.exists(os.path.dirname(db_path)):
        logger.warning(
            "Directorio de KUZU_DB_PATH no existe: %s", os.path.dirname(db_path)
        )
        return False
    if not os.path.exists(db_path):
        logger.warning("KUZU_DB_PATH no existe, se creará al bootstrap: %s", db_path)
    return True


# Bootstrap perezoso para estabilidad multi-CLI
_orchestrator = None
_proxy_manager = None


def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        if not _validate_db_path(KUZU_DB_PATH):
            logger.error("No se puede inicializar orquestador: KUZU_DB_PATH inválido")
            _write_readiness("bootstrap_failed")
            return None
        try:
            _orchestrator = bootstrap_orchestrator(KUZU_DB_PATH, AIWG_DIR)
        except RuntimeError as e:
            if "Could not set lock on file" in str(e):
                logger.critical(f"Kuzu DB locked: {e}")
                _write_readiness("db_locked")
            else:
                logger.critical(f"Bootstrap error: {e}")
                _write_readiness("bootstrap_failed")
            _log_quarantine("BOOTSTRAP_FAILED", str(e))
            _orchestrator = None
        except Exception as e:
            logger.critical(f"Bootstrap inesperado: {e}")
            _write_readiness("bootstrap_failed")
            _log_quarantine("BOOTSTRAP_FAILED", str(e))
            _orchestrator = None
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
    _write_readiness("ready")

    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Gateway detenido por señal de interrupción")
        _write_readiness("degraded")
    except Exception as e:
        logger.critical(f"Gateway Crash: {e}")
        _log_quarantine("GATEWAY_CRASH", str(e))
        _write_readiness("bootstrap_failed")
        sys.exit(1)
    finally:
        import asyncio

        if _proxy_manager:
            try:
                asyncio.run(asyncio.wait_for(_proxy_manager.shutdown(), timeout=2.0))
            except Exception:
                pass
        _write_readiness("degraded")
