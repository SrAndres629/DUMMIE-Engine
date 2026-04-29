import sys
import os
import time
import subprocess
import shutil

# Asegurar que podemos importar los módulos de la capa nervous
sys.path.append('layers/l1_nervous')
from memory_ipc import ArrowMemoryBridge, MemoryPlaneError

def test_industrial_e2e():
    print("=== DUMMIE INDUSTRIAL VERIFICATION - SMOKE E2E ===")
    
    SOCKET_PATH = "/tmp/dummie_industrial.sock"
    DB_PATH = "/tmp/dummie_ind_kuzu/state.db"
    
    # Limpieza total antes de empezar
    if os.path.exists(SOCKET_PATH): os.remove(SOCKET_PATH)
    parent_dir = os.path.dirname(DB_PATH)
    if os.path.exists(parent_dir):
        shutil.rmtree(parent_dir, ignore_errors=True)
    os.makedirs(parent_dir, exist_ok=True)
    
    bridge = ArrowMemoryBridge(SOCKET_PATH)
    
    # 1. Test OFFLINE (Error Propagation)
    print("[1/3] Testing Offline Error Propagation...")
    try:
        bridge.ipc.execute("RETURN 1")
        print("FAILED: Expected exception but query succeeded?")
        return False
    except MemoryPlaneError as e:
        print(f"OK: Caught expected error: {e.code}")
    except Exception as e:
        print(f"FAILED: Caught unexpected exception type: {type(e).__name__}")
        return False

    # 2. Test ONLINE (Boot & Connect)
    print("[2/3] Testing Online Boot and Connect...")
    env = os.environ.copy()
    env["MEMORY_SOCKET_PATH"] = SOCKET_PATH
    env["KUZU_DB_PATH"] = DB_PATH
    
    # Arrancamos el servidor (Binario si existe, si no go run)
    binary_path = "./bin/memory_server"
    if os.path.exists(os.path.join("layers/l1_nervous", binary_path)):
        cmd = [binary_path]
    else:
        cmd = ["go", "run", "cmd/memory/main.go"]
        
    proc = subprocess.Popen(
        cmd,
        cwd="layers/l1_nervous",
        env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True
    )
    
    # Reintentos para el Heartbeat (Determinismo Industrial)
    max_retries = 10
    connected = False
    for i in range(max_retries):
        time.sleep(1.5)
        print(f"     Attempting heartbeat {i+1}/{max_retries}...")
        if bridge.heartbeat():
            connected = True
            break
            
    if not connected:
        print("FAILED: Could not establish heartbeat with Memory Plane.")
        out, err = proc.communicate(timeout=1)
        print(f"--- Server STDOUT ---\n{out}")
        print(f"--- Server STDERR ---\n{err}")
        proc.terminate()
        return False
    
    print("OK: Heartbeat established.")
    
    # 3. Test QUERY (Data Integrity)
    print("[3/3] Testing Typed Query Execution...")
    try:
        res = bridge.ipc.execute("RETURN 'INDUSTRIAL_PASS' as result")
        data = res.get_next()
        if data[0] == "INDUSTRIAL_PASS":
            print(f"OK: Received expected data: {data[0]}")
            success = True
        else:
            print(f"FAILED: Received unexpected data: {data}")
            success = False
    except Exception as e:
        print(f"FAILED: Error during query execution: {str(e)}")
        success = False
    finally:
        # Apoptosis
        proc.terminate()
        proc.wait()
        if os.path.exists(SOCKET_PATH): os.remove(SOCKET_PATH)
        
    return success

if __name__ == "__main__":
    if test_industrial_e2e():
        print("\nVERDICT: PASS")
        sys.exit(0)
    else:
        print("\nVERDICT: FAIL")
        sys.exit(1)
