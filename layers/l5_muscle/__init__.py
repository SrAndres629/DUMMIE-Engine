try:
    from .mcp_driver import MCPDriver
    from .manager import SandboxManager
    from .mcp_driver import MCPDriver as MuscleDriver
except ImportError:
    from mcp_driver import MCPDriver
    from manager import SandboxManager
    from mcp_driver import MCPDriver as MuscleDriver
