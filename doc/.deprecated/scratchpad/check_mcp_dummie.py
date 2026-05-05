import asyncio
import os

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main() -> None:
    root = os.getcwd()
    env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": "layers/l2_brain:layers/l1_nervous:layers/l3_shield",
        "DUMMIE_ROOT_DIR": root,
        "DUMMIE_AIWG_DIR": os.path.join(root, ".aiwg"),
        "DUMMIE_MCP_CONFIG_PATH": os.path.join(root, "dummie_gateway_config.json"),
    }
    server = StdioServerParameters(
        command="layers/l2_brain/.venv/bin/python",
        args=["layers/l1_nervous/mcp_server.py"],
        cwd=root,
        env=env,
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("TOOLS", len(tools.tools))
            print("TOOL_NAMES", ",".join(tool.name for tool in tools.tools))
            for name in ("brain_ping", "calibrate_neural_links", "list_remote_servers"):
                result = await session.call_tool(name, {})
                print(f"CALL {name} isError={result.isError}")
                print("".join(getattr(item, "text", "") for item in result.content))


if __name__ == "__main__":
    asyncio.run(main())
