import sys
import os
import time
import subprocess
import signal

sys.path.append('layers/l1_nervous')
from memory_ipc import ArrowMemoryBridge, MemoryPlaneError

def test_smoke_flow():
    print("[TEST] Iniciando Smoke E2E Flow...")
    
    # 1. Verificar fallo ruidoso (Servidor apagado)
    bridge = ArrowMemoryBridge("/tmp/dummie_smoke.sock")
    print("[TEST] 1. Verificando fallo con servidor offline...")
    if not bridge.heartbeat():
        print("[PASS] Heartbeat falló correctamente (Servidor offline).")
    
    try:
        bridge.ipc.execute("RETURN 1")
    except MemoryPlaneError as e:
        print(f"[PASS] Capturada excepción estructurada: {e.code}")
    except Exception as e:
        print(f"[FAIL] Se esperaba MemoryPlaneError, se obtuvo: {type(e).__name__}")

    # 2. Iniciar Servidor (Simulado vía subprocess)
    print("[TEST] 2. Iniciando Memory Plane Server...")
    env = os.environ.copy()
    env["MEMORY_SOCKET_PATH"] = "/tmp/dummie_smoke.sock"
    # Usamos una DB temporal para no chocar con la real
    env["KUZU_DB_PATH"] = "/tmp/dummie_smoke_kuzu"
    
    proc = subprocess.Popen(
        ["go", "run", "cmd/memory/main.go"],
        cwd="layers/l1_nervous",
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    
    time.sleep(5) # Esperar arranque y fencing
    
    try:
        print("[TEST] 3. Intentando consulta exitosa...")
        if bridge.heartbeat():
            res = bridge.ipc.execute("RETURN 'SOVEREIGN' as status")
            data = res.get_next()
            print(f"[PASS] Resultado recibido: {data[0]}")
            
            # 4. Forzar caída y verificar error
            print("[TEST] 4. Simulando caída de servidor...")
            proc.terminate()
            time.sleep(1)
            
            try:
                bridge.ipc.execute("RETURN 1")
            except MemoryPlaneError as e:
                print(f"[PASS] Error de caída detectado: {e.code}")
        else:
            print("[FAIL] El servidor no respondió al heartbeat.")
    finally:
        if proc.poll() is None:
            proc.kill()
        if os.path.exists("/tmp/dummie_smoke.sock"):
            os.remove("/tmp/dummie_smoke.sock")

if __name__ == "__main__":
    test_smoke_flow()
