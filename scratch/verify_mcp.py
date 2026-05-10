import asyncio
import json
from mcp.server.fastmcp import FastMCP

# Internal registry
internal_mcp = FastMCP("Internal")

# Simulate a domain registration
@internal_mcp.tool()
def sample_tool(param1: str, param2: int = 5) -> str:
    """A sample tool for testing."""
    return f"{param1} - {param2}"

# Main Server
main_mcp = FastMCP("Gateway")

@main_mcp.tool()
async def dummie_discover_capabilities() -> str:
    """Discover capabilities"""
    tools = internal_mcp._tool_manager.list_tools()
    output = ["Local Capabilities:"]
    for t in tools:
        output.append(f"- local.{t.name}: {t.description}")
    return "\n".join(output)

@main_mcp.tool()
async def dummie_analyze_capability(target: str) -> str:
    """Analyze a capability"""
    if target.startswith("local."):
        name = target.split("local.")[1]
        tools = internal_mcp._tool_manager.list_tools()
        for t in tools:
            if t.name == name:
                return f"Schema for {target}:\n{json.dumps(t.parameters, indent=2)}"
    return "Not found"

@main_mcp.tool()
async def dummie_execute_capability(target: str, arguments: dict) -> str:
    """Execute capability"""
    if target.startswith("local."):
        name = target.split("local.")[1]
        tools = internal_mcp._tool_manager.list_tools()
        for t in tools:
            if t.name == name:
                # Need to convert dictionary args to keyword args using t.run
                res = await t.run(arguments)
                return str(res)
    return "Not found"

async def main():
    print(await dummie_discover_capabilities())
    print("---")
    print(await dummie_analyze_capability("local.sample_tool"))
    print("---")
    res = await dummie_execute_capability("local.sample_tool", {"param1": "SUCCESS"})
    print("Execution:", res)

asyncio.run(main())
