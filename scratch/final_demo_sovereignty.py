
import os
import sys
import json
import time

# Forzar ruta canónica
ROOT_DIR = "/home/jorand/Escritorio/DUMMIE Engine"
os.environ["MEMORY_SOCKET_PATH"] = os.path.join(ROOT_DIR, ".aiwg/sockets/flight.sock")

sys.path.append(os.path.join(ROOT_DIR, "layers/l2_brain"))
sys.path.append(os.path.join(ROOT_DIR, "layers/l1_nervous"))

from memory_ipc import ArrowMemoryBridge
from adapters import KuzuRepository
from models import MemoryNode4D, AuthorityLevel, IntentType

def demonstrate():
    print("=== [DEMOSTRACIÓN DE SOBERANÍA 4D] ===")
    
    # 1. Conexión vía IPC (Optimizado/Sincronizado)
    bridge = ArrowMemoryBridge()
    if not bridge.heartbeat():
        print("❌ FALLO: No se pudo conectar al Memory Plane.")
        return

    print("✅ Conectado al Memory Plane (IPC Mode).")
    repo = KuzuRepository(db=bridge)
    
    # 2. Escritura de Prueba
    test_payload = f"Prueba de Soberanía {int(time.time())}: El motor 4D es funcional al 100%."
    causal_hash, cypher = MemoryNode4D.build_create_cypher(
        parent_hash=repo.get_last_leaf_hash(),
        locus_x="demo.sovereignty",
        locus_y="IPC",
        locus_z="L2_BRAIN",
        lamport_t=int(time.time()),
        authority_a=AuthorityLevel.AGENT.value,
        intent_i=IntentType.CRYSTALLIZATION.value,
        payload=test_payload
    )
    
    print(f"[*] Escribiendo nodo causal: {causal_hash}...")
    repo.query(cypher)
    print("✅ Escritura completada exitosamente.")

    # 3. Lectura Semántica (Similitud)
    print("[*] Verificando persistencia semántica...")
    # Buscamos algo parecido a nuestro payload
    results = repo.find_similar_nodes("motor 4D funcional", limit=1)
    
    if results and test_payload in results[0]['payload']:
        print(f"✅ VERIFICACIÓN PASADA: Nodo recuperado con éxito.")
        print(f"   Payload: {results[0]['payload']}")
        print(f"   Intent: {results[0]['intent']}")
    else:
        print("❌ VERIFICACIÓN FALLIDA: No se encontró el nodo.")

if __name__ == "__main__":
    demonstrate()
