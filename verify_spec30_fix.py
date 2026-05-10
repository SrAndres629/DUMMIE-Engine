import os
import sys
import time
import subprocess
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify-spec30")

ROOT_DIR = "/home/jorand/Escritorio/DUMMIE Engine"
SOCKET_PATH = "/tmp/dummie_memory.sock"
DB_PATH = os.path.join(ROOT_DIR, ".aiwg/memory/loci.db")
SERVER_BIN = os.path.join(ROOT_DIR, "bin/memory_server")

def test_memory_plane():
    logger.info("=== Iniciando Verificación de SPEC-30 (Arrow Data Plane) ===")

    # 1. Asegurar que el servidor no esté corriendo
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    # 2. Iniciar el Memory Server en segundo plano
    logger.info(f"[*] Lanzando Memory Server: {SERVER_BIN}")
    server_proc = subprocess.Popen(
        [SERVER_BIN],
        env={**os.environ, "KUZU_DB_PATH": DB_PATH, "MEMORY_SOCKET_PATH": SOCKET_PATH},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        # Esperar a que el socket aparezca
        max_retries = 10
        for i in range(max_retries):
            if os.path.exists(SOCKET_PATH):
                logger.info("[✓] Memory Plane Socket detectado.")
                break
            logger.info(f"[*] Esperando socket... ({i+1}/{max_retries})")
            time.sleep(1)
        else:
            logger.error("[!] El socket no apareció. Fallo en el inicio del servidor.")
            return False

        # 3. Probar conexión desde Python usando el proxy
        logger.info("[*] Probando conexión desde Python (IPC Client)...")
        sys.path.append(os.path.join(ROOT_DIR, "layers/l1_nervous"))
        from memory_ipc import ArrowMemoryBridge

        bridge = ArrowMemoryBridge(SOCKET_PATH)
        if bridge.heartbeat():
            logger.info("[✓] Heartbeat exitoso. Conexión IPC establecida.")
        else:
            logger.error("[!] Heartbeat fallido.")
            return False

        # 4. Probar consulta Cypher a través del proxy
        logger.info("[*] Ejecutando consulta de prueba...")
        results = bridge.ipc.execute("RETURN 1 as val")
        if results and len(results) > 0:
            logger.info(f"[✓] Consulta exitosa. Resultado: {results}")
        else:
            logger.error("[!] La consulta no devolvió resultados.")
            return False

        logger.info("=== [ÉXITO] SPEC-30 validado y operativo ===")
        return True

    finally:
        logger.info("[*] Limpiando procesos...")
        server_proc.terminate()
        server_proc.wait()
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

if __name__ == "__main__":
    success = test_memory_plane()
    sys.exit(0 if success else 1)
