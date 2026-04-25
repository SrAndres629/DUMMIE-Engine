import logging
from mcp.server.fastmcp import FastMCP
from .application.use_cases import BrainToolUseCases
from .tools_impl.core import register_core_tools
from .tools_impl.gateway import register_gateway_tools
from .tools_impl.swarm import register_swarm_tools
from .tools_impl.nervous import register_nervous_tools

logger = logging.getLogger("dummie-mcp.tools")

def register_tools(mcp: FastMCP, orchestrator, proxy_manager, root_dir: str):
    """Dispatcher para el registro de herramientas (Arquitectura Hexagonal)."""
    
    logger.info("Iniciando registro de herramientas (L1-Hexagonal)...")
    
    # Capa de Aplicación
    use_cases = BrainToolUseCases(orchestrator, proxy_manager)

    # Registro por Dominio
    register_core_tools(mcp, use_cases, root_dir)
    register_gateway_tools(mcp, use_cases)
    register_swarm_tools(mcp, use_cases, root_dir)
    register_nervous_tools(mcp, use_cases, root_dir)
    
    logger.info("Registro de herramientas completado exitosamente.")
