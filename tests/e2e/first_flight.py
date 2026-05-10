import asyncio
import uuid
from dummie.brain.core.consensus_graph import build_consensus_graph, ConsensusState

async def test_first_flight():
    """
    Simulación de la Prueba de Vuelo (E2E).
    Cruza el Grafo de Consenso (L2) invocando gRPC (L4) y NATS (L1).
    """
    print("\n=== INICIANDO FIRST FLIGHT TEST (DUMMIE Engine) ===\n")
    
    # 1. Configurar Tarea Inicial
    state = ConsensusState(
        task_id=str(uuid.uuid4()),
        input_prompt="Refactorizar el sistema de autenticación para usar JWT en el monorepo."
    )
    
    # 2. Compilar y Ejecutar el Grafo
    graph = build_consensus_graph()
    
    print(f"[E2E] Ejecutando Grafo de Consenso para Tarea: {state.task_id}")
    
    async for output in graph.astream(state):
        for node_name, node_state in output.items():
            print(f"--- Nodo Ejecutado: {node_name} ---")
            if node_state.current_intent:
                print(f"Intención: {node_state.current_intent.intent_type} en {node_state.current_intent.target_resource}")
                print(f"Auditor: {'✅' if node_state.auditor_approved else '❌'} - {node_state.auditor_feedback}")
                print(f"CTO: {'✅' if node_state.cto_approved else '❌'} - {node_state.cto_feedback}")
    
    print("\n=== PRUEBA DE VUELO COMPLETADA ESTRUCTURALMENTE ===")

if __name__ == "__main__":
    asyncio.run(test_first_flight())
