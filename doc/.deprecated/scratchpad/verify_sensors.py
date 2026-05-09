import asyncio
import json
import os
import sys

# Asegurar PYTHONPATH
sys.path.insert(0, "/home/jorand/Escritorio/DUMMIE Engine/layers/l1_nervous")
sys.path.insert(0, "/home/jorand/Escritorio/DUMMIE Engine/layers/l2_brain")

from mcp_proxy import MCPProxyManager

async def test_sensor(name, config_path):
    print(f"\n=== Testing sensor: {name} ===")
    manager = MCPProxyManager(config_path)
    
    try:
        # get_tools_for_server llamará internamente a _ensure_ready y poblará la cache
        print(f"Attempting to fetch tools for {name}...")
        tools = await manager.get_tools_for_server(name)
        
        if tools:
            print(f"SUCCESS: Fetched {len(tools)} tools from {name}:")
            for t in tools:
                print(f"  - {t.get('name')}")
            return True
        else:
            print(f"FAILED: No tools returned for {name} or server failed to start.")
            return False
    except Exception as e:
        print(f"FAILED to get tools for {name}: {e}")
        return False

async def main():
    config_path = "/home/jorand/Escritorio/DUMMIE Engine/dummie_gateway_config.json"
    
    # Test Phoenix
    phoenix_ok = await test_sensor("phoenix", config_path)
    
    # Test Sentry
    sentry_ok = await test_sensor("sentry", config_path)
    
    if phoenix_ok and sentry_ok:
        print("\nALL SENSORS VERIFIED SUCCESSFULLY.")
        sys.exit(0)
    else:
        print("\nSENSOR VERIFICATION FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
