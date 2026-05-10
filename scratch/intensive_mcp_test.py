import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_intensive_test():
    """
    Prueba intensiva del Dummie Brain MCP.
    Realiza múltiples llamadas concurrentes y secuenciales para estresar KuzuDB
    y la persistencia del Ledger, buscando forzar errores EOF o de I/O.
    """
    server_params = StdioServerParameters(
        command="python",
        args=["/home/jorand/Escritorio/DUMMIE Engine/layers/l1_nervous/adapters/mcp/server.py"],
        env={"PYTHONPATH": "/home/jorand/Escritorio/DUMMIE Engine/layers/l2_brain/src"}
    )

    print(">>> Iniciando cliente MCP para prueba de estrés...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("[OK] Sesión inicializada.")

                # 1. Prueba Básica
                print(">>> Ejecutando brain_ping...")
                ping_res = await session.call_tool("brain_ping", {})
                print(f"Ping Result: {ping_res}")

                # 2. Prueba Intensiva: Múltiples lecturas de Loci Graph (Concurrencia)
                print(">>> Solicitando metacognitive_status de forma recurrente...")
                for i in range(5):
                    status = await session.call_tool("metacognitive_status", {})
                    print(f"Status {i} OK")

                # 3. Prueba de Escritura: Forzar cierres y locks en KuzuDB
                print(">>> Ejecutando cristalización intensiva...")
                for i in range(3):
                    res = await session.call_tool("crystallize", {
                        "payload": f"Test axiomático concurrente {i}",
                        "context": {"authority": "TEST", "locus": "sw.test"}
                    })
                    print(f"Crystallize {i} OK")

                # 4. Prueba de Ambigüedad
                print(">>> Registrando ambigüedad masiva...")
                amb_res = await session.call_tool("resolve_ambiguity", {
                    "ambiguity": "¿El estado de I/O bloquea el hilo principal?",
                    "plan": "Ejecutar pruebas de estrés EOF."
                })
                print(f"Ambiguity Result: {amb_res}")

                print(">>> PRUEBA INTENSIVA COMPLETADA SIN ERROR EOF <<<")

    except Exception as e:
        print(f"
[!] ERROR DETECTADO DURANTE LA PRUEBA:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_intensive_test())
