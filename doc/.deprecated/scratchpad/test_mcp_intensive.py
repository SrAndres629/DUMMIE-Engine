import os
import sys
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp():
    server_params = StdioServerParameters(
        command="/home/jorand/Escritorio/DUMMIE Engine/layers/l2_brain/.venv/bin/python",
        args=["/home/jorand/Escritorio/DUMMIE Engine/layers/l1_nervous/mcp_server.py"],
        env={**os.environ, 
             "DUMMIE_ROOT_DIR": "/home/jorand/Escritorio/DUMMIE Engine",
             "DUMMIE_AIWG_DIR": "/home/jorand/Escritorio/DUMMIE Engine/.aiwg",
             "DUMMIE_KUZU_DB_PATH": "/home/jorand/Escritorio/DUMMIE Engine/.aiwg/memory/loci_agent.db",
             "PYTHONPATH": "/home/jorand/Escritorio/DUMMIE Engine/layers/l2_brain/src"}
    )
    
    print("Iniciando conexión con DUMMIE Brain MCP...")
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✓ MCP Inicializado correctamente. (No hubo Error EOF o crash inicial)")
                
                # Test resources
                print("
--- Probando Resources ---")
                resources = await session.list_resources()
                for res in resources.resources:
                    print(f"Leyendo recurso: {res.uri}")
                    try:
                        data = await session.read_resource(res.uri)
                        print(f"  [OK] Datos leídos: {len(data.contents[0].text)} caracteres.")
                    except Exception as e:
                        print(f"  [Error] {e}")
                
                # Test tools
                print("
--- Probando Tools ---")
                tools = await session.list_tools()
                for t in tools.tools:
                    print(f"Herramienta disponible: {t.name}")
                    
                # Call calibrate (intensive system check)
                print("
Ejecutando 'calibrate_neural_links' para forzar carga...")
                result = await session.call_tool("calibrate_neural_links", {})
                print(f"Resultado:
{result.content[0].text}")
                
                print("
✓ Prueba intensiva completada. Protocolo Stdio (JSON-RPC) se mantuvo estable.")
    except Exception as e:
        print(f"❌ Error durante la prueba (Posible EOF o desconexión): {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp())
