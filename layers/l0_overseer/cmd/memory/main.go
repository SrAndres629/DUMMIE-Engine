package main

import (
	"log"
	"os"

	"io.dummie.v2/overseer/internal/memory"
)

func main() {
	dbPath := os.Getenv("KUZU_DB_PATH")
	if dbPath == "" {
		dbPath = "/home/jorand/Escritorio/DUMMIE Engine/.aiwg/memory/kuzu"
	}
	
	socketPath := os.Getenv("MEMORY_SOCKET_PATH")
	if socketPath == "" {
		socketPath = "/tmp/dummie_memory.sock"
	}

	log.Printf("[L0-MEMORY] Iniciando Servidor de Memoria Compartida...")
	log.Printf("[L0-MEMORY] DB Path: %s", dbPath)
	log.Printf("[L0-MEMORY] Socket: %s", socketPath)

	if err := memory.StartFlightServer(dbPath, socketPath); err != nil {
		log.Printf("[L0-MEMORY] ERROR CRÍTICO: No se pudo iniciar el servidor.")
		log.Printf("[L0-MEMORY] Causa probable: La base de datos está bloqueada por otro proceso.")
		log.Printf("[L0-MEMORY] Solución: Ejecuta 'scripts/vanguard_lock_resolver.sh' para liberar bloqueos.")
		log.Fatalf("[L0-MEMORY] Detalles: %v", err)
	}
}
