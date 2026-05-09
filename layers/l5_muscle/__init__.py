__spec_id__ = "DE-V2-L5-01"
__spec_id__ = "DE-V2-L5-20"
__spec_id__ = "DE-V2-L5-16"
__spec_id__ = "DE-V2-L5-32"
try:
    from .mcp_driver import MCPDriver
    from .manager import SandboxManager
    from .mcp_driver import MCPDriver as MuscleDriver
except ImportError:
    from mcp_driver import MCPDriver
    from manager import SandboxManager
    from mcp_driver import MCPDriver as MuscleDriver
