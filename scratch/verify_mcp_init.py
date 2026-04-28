import asyncio
from mcp.server.fastmcp import FastMCP
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), "layers/l1_nervous"))

from tools import register_tools
from application.use_cases import BrainToolUseCases

class MockOrchestrator:
    lamport_clock = 0

class MockProxyManager:
    servers = {"git": {}}
    async def get_tools_for_server(self, name):
        return [{"name": "git_status", "description": "Status"}]
    async def call_tool(self, server, tool, args):
        return "OK"

mcp = FastMCP("Test")
register_tools(mcp, MockOrchestrator(), MockProxyManager(), os.getcwd())

async def main():
    tools = await mcp._tool_manager.list_tools()
    print("Exposed Tools:")
    for t in tools:
        print(t.name)

asyncio.run(main())
