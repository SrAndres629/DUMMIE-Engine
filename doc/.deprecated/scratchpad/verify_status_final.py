import os
import sys
from pathlib import Path

# Configurar entorno
ROOT_DIR = "/home/jorand/Escritorio/DUMMIE Engine"
sys.path.append(os.path.join(ROOT_DIR, "layers/l2_brain"))
sys.path.append(os.path.join(ROOT_DIR, "layers/l1_nervous"))

os.environ["DUMMIE_ROOT_DIR"] = ROOT_DIR
os.environ["MEMORY_SOCKET_PATH"] = "/tmp/dummie_flight.sock"

from bootstrap import bootstrap_orchestrator

print("=== VERIFICACIÓN DE ESTADO INDUSTRIAL ===")
aiwg_dir = os.path.join(ROOT_DIR, ".aiwg")
kuzu_path = os.path.join(aiwg_dir, "memory/loci.db")

orchestrator = bootstrap_orchestrator(kuzu_path, aiwg_dir)

status = "Optimal" if not orchestrator.event_store.read_only else "Degraded"
print(f"Status Detectado: {status}")

if status == "Optimal":
    print("[✓] El Memory Plane está respondiendo correctamente.")
    # Probar una consulta real
    try:
        res = orchestrator.event_store.conn.execute("RETURN 1").get_next()
        print(f"[✓] Consulta Kuzu (IPC): SUCCESS ({res})")
    except Exception as e:
        print(f"[!] Fallo en consulta IPC: {e}")
else:
    print("[!] El sistema sigue en modo DEGRADADO.")

print("==========================================")
