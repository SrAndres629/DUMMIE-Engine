import asyncio
import os
import sys

# Setup Paths
ROOT_DIR = os.environ.get("DUMMIE_ROOT", "/opt/dummie-engine")
for layer in ["l1_nervous", "l2_brain", "l3_shield"]:
    sys.path.append(os.path.join(ROOT_DIR, "layers", layer))

from mcp_proxy import MCPProxyManager
from bootstrap import bootstrap_orchestrator


async def test_integration():
    print("🚀 Testing Obsidian/Socraticode Integration...")

    AIWG_DIR = os.path.join(ROOT_DIR, ".aiwg")
    KUZU_DB_PATH = os.path.join(AIWG_DIR, "memory/loci.db")
    GATEWAY_CONFIG = os.path.join(ROOT_DIR, "dummie_gateway_config.json")

    # 1. Proxy Manager
    proxy = MCPProxyManager(GATEWAY_CONFIG)
    print(f"Proxy Servers: {list(proxy.servers.keys())}")

    if "socraticode" in proxy.servers and "obsidian" in proxy.servers:
        print("✅ Servers registered in Proxy.")
    else:
        print("❌ Servers missing from Proxy.")

    # 2. Orchestrator
    orch = bootstrap_orchestrator(KUZU_DB_PATH, AIWG_DIR)
    orch.set_mcp_gateway(proxy)

    if orch.obsidian and orch.socraticode:
        print("✅ SDKs Materialized in Orchestrator.")
    else:
        print("❌ SDKs FAILED to materialize.")

    if orch.auto_evolver.socraticode:
        print("✅ Socraticode injected in AutoEvolver.")

    if orch.entity_voice.obsidian:
        print("✅ Obsidian injected in EntityVoice.")

    print("🚀 Verification Complete.")


if __name__ == "__main__":
    asyncio.run(test_integration())
