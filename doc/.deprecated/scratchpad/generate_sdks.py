import asyncio
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

# Asegurar PYTHONPATH
sys.path.insert(0, "/home/jorand/Escritorio/DUMMIE Engine/layers/l1_nervous")
sys.path.insert(0, "/home/jorand/Escritorio/DUMMIE Engine/layers/l2_brain")

from mcp_proxy import MCPProxyManager
from sdk_generator import DynamicSDKGenerator

async def main():
    config_path = "/home/jorand/Escritorio/DUMMIE Engine/dummie_gateway_config.json"
    output_dir = "/home/jorand/Escritorio/DUMMIE Engine/layers/l1_nervous/generated"
    
    manager = MCPProxyManager(config_path)
    generator = DynamicSDKGenerator(manager, output_dir)
    
    print("Arrancando servidores para introspección...")
    # Esperar a que los servidores arranquen
    await asyncio.sleep(10)
    
    await generator.generate_all()
    print("Generación finalizada.")

if __name__ == "__main__":
    asyncio.run(main())
