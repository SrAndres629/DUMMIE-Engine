import sys
import os
import time
import subprocess
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify-spec30")

# Rutas
ROOT_DIR = "/home/jorand/Escritorio/DUMMIE Engine"
sys.path.append(os.path.join(ROOT_DIR, "layers/l1_nervous"))
sys.path.append(os.path.join(ROOT_DIR, "layers/l2_brain"))

from memory_ipc import ArrowMemoryBridge
from adapters import KuzuRepository

def run_verification():
    SOCKET_PATH = "/tmp/dummie_memory_test.sock"
    DB_PATH = os.path.join(ROOT_DIR, ".aiwg/memory/kuzu")
    SERVER_BIN = os.path.join(ROOT_DIR, "bin/memory_server")

    # Asegurar que el socket no exista al inicio
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    # 1. Test Fallback (Servidor apagado)
    logger.info("--- TEST 1: Heartbeat Fallback ---")
    bridge = ArrowMemoryBridge(SOCKET_PATH)
    if not bridge.heartbeat():
        logger.info("[OK] Heartbeat detectó correctamente que el servidor está apagado.")
    else:
        logger.error("[FAIL] Heartbeat dio positivo con servidor apagado.")
        return

    # 2. Iniciar Servidor Go
    logger.info("--- TEST 2: Conexión y Fidelidad ---")
    if not os.path.exists(SERVER_BIN):
        logger.error(f"[FAIL] Binario del servidor no encontrado en {SERVER_BIN}. ¿Ejecutaste 'make build-l0'?")
        return

    env = os.environ.copy()
    env["MEMORY_SOCKET_PATH"] = SOCKET_PATH
    env["KUZU_DB_PATH"] = DB_PATH
    # Importante: LD_LIBRARY_PATH debe apuntar a donde estén las .so de Kuzu
    LIB_PATH = os.path.join(ROOT_DIR, "shared/lib/kuzu")
    env["LD_LIBRARY_PATH"] = f"{LIB_PATH}:{env.get('LD_LIBRARY_PATH', '')}"
    
    proc = subprocess.Popen([SERVER_BIN], env=env)
    time.sleep(2) # Esperar a que inicie

    try:
        if bridge.heartbeat():
            logger.info("[OK] Heartbeat detectó el servidor encendido.")
        else:
            logger.error("[FAIL] Heartbeat falló con el servidor encendido.")
            return

        # Probar repositorio
        repo = KuzuRepository(db=bridge)
        
        # Consulta de prueba
        logger.info("Ejecutando consulta de prueba...")
        res = repo.query("RETURN 1 as val, 'DUMMIE' as name")
        
        if res and res.has_next():
            row = res.get_next()
            logger.info(f"Fila recibida: {row}")
            # El orden puede variar por el map de Go, pero los valores deben ser correctos
            if 1 in row and 'DUMMIE' in row:
                logger.info("[OK] Fidelidad de datos mantenida (Tipos preservados).")
            else:
                logger.error(f"[FAIL] Datos corruptos o inesperados: {row}")
        else:
            logger.error("[FAIL] No se recibieron resultados.")

    except Exception as e:
        logger.error(f"[CRITICAL] Error durante la prueba: {str(e)}")
    finally:
        logger.info("Limpiando...")
        proc.terminate()
        proc.wait()
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

if __name__ == "__main__":
    run_verification()
