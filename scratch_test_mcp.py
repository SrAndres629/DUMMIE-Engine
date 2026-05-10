import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test():
    params = StdioServerParameters(
        command="/home/jorand/Escritorio/DUMMIE Engine/layers/l2_brain/.venv/bin/python",
        args=["/home/jorand/Escritorio/DUMMIE Engine/layers/l1_nervous/mcp_server.py"],
        env={
            "DUMMIE_ROOT_DIR": "/home/jorand/Escritorio/DUMMIE Engine",
            "DUMMIE_AIWG_DIR": "/home/jorand/Escritorio/DUMMIE Engine/.aiwg",
            "DUMMIE_KUZU_DB_PATH": "/home/jorand/Escritorio/DUMMIE Engine/.aiwg/memory/loci.db",
            "PYTHONPATH": "/home/jorand/Escritorio/DUMMIE Engine/layers/l2_brain:/home/jorand/Escritorio/DUMMIE Engine/layers/l1_nervous:/home/jorand/Escritorio/DUMMIE Engine/layers/l3_shield",
            "DUMMIE_MCP_CONFIG_PATH": "/home/jorand/Escritorio/DUMMIE Engine/dummie_agent_config.json"
        }
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Initialized")
            result = await session.call_tool("dummie_discover_capabilities", {"query": "*"})
            print(result)

asyncio.run(test())
