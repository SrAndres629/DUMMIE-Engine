import multiprocessing
import os
import sys
import json
import time
sys.path.append('layers/l1_nervous')
from utils import AtomicLedgerWriter

LEDGER_PATH = "/home/jorand/Escritorio/DUMMIE Engine/.aiwg/memory/swarm_race_test.jsonl"

def worker(worker_id):
    for i in range(100):
        entry = {
            "worker": worker_id,
            "count": i,
            "msg": f"Race condition test from worker {worker_id}"
        }
        AtomicLedgerWriter.append_entry(LEDGER_PATH, entry)

if __name__ == "__main__":
    if os.path.exists(LEDGER_PATH):
        os.remove(LEDGER_PATH)
        
    print(f"[TEST] Iniciando Swarm Race Test (50 workers, 100 entries each)...")
    processes = []
    for i in range(50):
        p = multiprocessing.Process(target=worker, args=(i,))
        processes.append(p)
        p.start()
        
    for p in processes:
        p.join()
        
    print(f"[TEST] Escritura finalizada. Verificando integridad del JSONL...")
    
    with open(LEDGER_PATH, "r") as f:
        lines = f.readlines()
        print(f"[INFO] Líneas totales: {len(lines)} (Esperadas: 5000)")
        
        # Validar cada línea como JSON válido
        valid_count = 0
        for line in lines:
            try:
                json.loads(line)
                valid_count += 1
            except:
                print(f"[FAIL] Línea corrupta detectada: {line}")
        
        if valid_count == 5000:
            print("[PASS] Swarm Race Integrity: 100% de los datos válidos y sin colisiones.")
        else:
            print(f"[FAIL] Se encontraron {5000 - valid_count} líneas corruptas.")
