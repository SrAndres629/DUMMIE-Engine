import asyncio
import os
import sys

# Setup Paths
ROOT_DIR = "/home/jorand/Escritorio/DUMMIE Engine"
for layer in ["l1_nervous", "l2_brain", "l3_shield"]:
    sys.path.append(os.path.join(ROOT_DIR, "layers", layer))

from mcp_proxy import MCPProxyManager
from orchestrator import CognitiveOrchestrator

async def test_integration():
    print("🚀 Testing Obsidian/Socraticode Integration...")
    
    # 1. Config Path Check
    config_path = os.path.join(ROOT_DIR, "dummie_gateway_config.json")
    print(f"Checking config: {config_path}")
    if os.path.exists(config_path):
        print("✅ Config found.")
    else:
        print("❌ Config NOT found.")
        return

    # 2. Proxy Manager Initialization
    proxy = MCPProxyManager(config_path)
    print(f"Proxy Servers: {list(proxy.servers.keys())}")
    
    if "socraticode" in proxy.servers and "obsidian" in proxy.servers:
        print("✅ Servers registered in Proxy.")
    else:
        print("❌ Servers missing from Proxy.")

    # 3. Orchestrator Integration
    orch = CognitiveOrchestrator(os.path.join(ROOT_DIR, ".aiwg/memory/loci.db"), os.path.join(ROOT_DIR, ".aiwg"))
    orch.set_mcp_gateway(proxy)
    
    if orch.obsidian and orch.socraticode:
        print("✅ SDKs Materialized in Orchestrator.")
    else:
        print("❌ SDKs FAILED to materialize.")

    if orch.auto_evolver.socraticode:
        print("✅ Socraticode injected in AutoEvolver.")
    
    if orch.entity_voice.obsidian:
        print("✅ Obsidian injected in EntityVoice.")

if __name__ == "__main__":
    asyncio.run(test_integration())
