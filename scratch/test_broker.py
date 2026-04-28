import asyncio
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

sys.path.insert(0, "/home/jorand/Escritorio/DUMMIE Engine/layers/l1_nervous")

from broker import EventBroker
from mcp_proxy import MCPProxyManager

async def test():
    broker = EventBroker()
    proxy = MCPProxyManager("/home/jorand/Escritorio/DUMMIE Engine/dummie_gateway_config.json")
    
    async def handle_mcp_call(data):
        server = data.get("server")
        tool = data.get("tool")
        args = data.get("args", {})
        print(f"[Broker] Procesando {server}.{tool}...")
        return await proxy.call_tool(server, tool, args)
        
    broker.subscribe("mcp.call", handle_mcp_call)
    
    print("Esperando arranque de servidores...")
    await asyncio.sleep(5)
    
    print("Lanzando peticiones concurrentes...")
    tasks = []
    for i in range(3):
        tasks.append(broker.send_command("mcp.call", {
            "server": "sequentialthinking",
            "tool": "sequentialthinking",
            "args": {
                "thought": f"Test concurrent engine {i}",
                "thoughtNumber": i + 1,
                "totalThoughts": 3,
                "nextThoughtNeeded": False
            }
        }))
        
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, r in enumerate(results):
        print(f"Resultado {i}: {r}")
        
    await broker.shutdown()
    await proxy.shutdown()

if __name__ == "__main__":
    asyncio.run(test())
