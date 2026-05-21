
import asyncio
import os
import sys
from pathlib import Path

# Setup paths to include layers
ROOT_DIR = os.getcwd()
sys.path.insert(0, ROOT_DIR)
for layer in ["l1_nervous", "l2_brain", "l3_shield"]:
    sys.path.insert(0, os.path.join(ROOT_DIR, "layers", layer))
sys.path.insert(0, os.path.join(ROOT_DIR, "layers", "l2_brain", "src"))

from layers.l1_nervous.mcp_proxy import MCPProxyManager

async def verify():
    config_path = os.path.join(ROOT_DIR, "dummie_gateway_config.json")
    print(f"Checking config at: {config_path}")

    proxy = MCPProxyManager(config_path)

    servers_to_test = ["sequentialthinking", "mcp-bash", "github", "sqlite", "browser-use"]

    for server in servers_to_test:
        print(f"\n--- Testing Server: {server} ---")
        try:
            tools = await proxy.get_tools_for_server(server)
            print(f"Success! Found {len(tools)} tools for {server}")
            if tools:
                print(f"First 3 tools: {[t['name'] for t in tools[:3]]}")
        except Exception as e:
            print(f"Failed to load {server}: {e}")

    await proxy.shutdown()

if __name__ == "__main__":
    asyncio.run(verify())
