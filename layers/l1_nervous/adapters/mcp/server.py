import os
import logging
import sys
from mcp.server.fastmcp import FastMCP

# DUMMIE Imports (Modularized)
from infrastructure.bootstrap import bootstrap_orchestrator, setup_shutdown_handlers
from handlers.tools import register_tools
from handlers.resources import register_resources
from mcp_proxy import MCPProxyManager

# 1. Configuration (Spec MCP-01)
ROOT_DIR = os.environ.get("DUMMIE_ROOT_DIR", "/home/jorand/Escritorio/DUMMIE Engine")
AIWG_DIR = os.environ.get("DUMMIE_AIWG_DIR", os.path.join(ROOT_DIR, ".aiwg"))
KUZU_DB_PATH = os.environ.get("DUMMIE_KUZU_DB_PATH", os.path.join(AIWG_DIR, "memory/loci.db"))
MCP_CONFIG_PATH = os.environ.get("DUMMIE_MCP_CONFIG_PATH", os.path.expanduser("~/.gemini/antigravity/mcp_config.registry.json"))

# 2. Logging Setup (Redirect to stderr per MCP standard)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("dummie-mcp.main")

# 3. Initialize FastMCP
mcp = FastMCP("DUMMIE-Brain-Gateway", 
              dependencies=["kuzu", "pydantic", "zstd", "mcp"])

# 4. Bootstrap Infrastructure
orchestrator = bootstrap_orchestrator(KUZU_DB_PATH, AIWG_DIR)
proxy_manager = MCPProxyManager(MCP_CONFIG_PATH)

# 5. Setup Signal Handlers & atexit
setup_shutdown_handlers(orchestrator, proxy_manager)

# 6. Register Handlers (Modular Refactor)
register_tools(mcp, orchestrator, proxy_manager, ROOT_DIR)
register_resources(mcp, orchestrator, proxy_manager, ROOT_DIR)

if __name__ == "__main__":
    logger.info("DUMMIE Brain Gateway initializing...")
    mcp.run()
