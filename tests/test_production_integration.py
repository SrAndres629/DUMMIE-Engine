
import asyncio
import os
import sys
import json
from pathlib import Path

# Setup paths
ROOT_DIR = os.getcwd()
sys.path.insert(0, ROOT_DIR)
for layer in ["l1_nervous", "l2_brain", "l3_shield"]:
    sys.path.insert(0, os.path.join(ROOT_DIR, "layers", layer))
sys.path.insert(0, os.path.join(ROOT_DIR, "layers", "l2_brain", "src"))

from layers.l1_nervous.mcp_proxy import MCPProxyManager
from layers.l1_nervous.mcp_server import mcp as brain_mcp

async def test_production_flow():
    print("--- 1. Verifying Gateway Config Parametrization ---")
    config_path = "dummie_gateway_config.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Check for hardcoded paths in args
    for s_name, s_cfg in config["mcpServers"].items():
        for arg in s_cfg.get("args", []):
            if isinstance(arg, str) and ("/home/jorand" in arg or "/media/datasets" in arg):
                print(f"FAILED: Hardcoded path in {s_name}: {arg}")
                # return # We continue to see other errors
    
    print("--- 2. Verifying Tool Discovery through Meta-Gateway ---")
    # We use the internal registry logic of mcp_server.py
    # Since we can't easily start the whole stdio server here, we test the proxy manager
    proxy = MCPProxyManager(config_path)
    
    # Test Shell (The new secure replacement for mcp-bash)
    print("Testing 'shell' (replacement for mcp-bash)...")
    try:
        tools = await proxy.get_tools_for_server("shell")
        print(f"Success! Shell tools: {[t['name'] for t in tools]}")
    except Exception as e:
        print(f"FAILED Shell: {e}")

    # Test Sequential Thinking
    print("Testing 'sequentialthinking'...")
    try:
        tools = await proxy.get_tools_for_server("sequentialthinking")
        print(f"Success! ST tools: {[t['name'] for t in tools]}")
    except Exception as e:
        print(f"FAILED ST: {e}")

    # Test SQLite subordination
    print("Testing 'sqlite' integration...")
    try:
        tools = await proxy.get_tools_for_server("sqlite")
        print(f"Success! SQLite tools: {[t['name'] for t in tools]}")
    except Exception as e:
        print(f"FAILED SQLite: {e}")

    await proxy.shutdown()

if __name__ == "__main__":
    asyncio.run(test_production_flow())
