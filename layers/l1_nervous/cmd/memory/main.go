package main

import (
	"log"
	"os"

	"github.com/nats-io/nats.go"
	"io.dummie.v2/nervous/internal/memory"
)

func main() {
	dbPath := os.Getenv("KUZU_DB_PATH")
	if dbPath == "" {
		dbPath = "../../.aiwg/memory/kuzu"
	}
	socketPath := os.Getenv("MEMORY_SOCKET_PATH")
	if socketPath == "" {
		socketPath = "/tmp/dummie_memory.sock"
	}
	natsURL := os.Getenv("NATS_URL")
	if natsURL == "" {
		natsURL = nats.DefaultURL
	}

	log.Printf("[L1-MEMORY] Iniciando Memory Plane (Data Plane)...")
	log.Printf("[L1-MEMORY] DB: %s", dbPath)
	log.Printf("[L1-MEMORY] Socket: %s", socketPath)

	// 1. ABRIR KUZU PRIMERO (Antes de cualquier otra librería pesada)
	if err := memory.ResolveStaleLocks(dbPath); err != nil {
		log.Printf("[L1-MEMORY] Fencing Error: %v", err)
	}
	
	// Usamos nil para NATS temporalmente hasta que el servidor esté listo
	// para evitar que la conexión NATS interfiera con la inicialización de Kuzu mmap
	server, err := memory.NewDummieMemoryServer(dbPath, nil)
	if err != nil {
		log.Fatalf("[L1-MEMORY] FATAL ERROR: failed to open kuzu at %s: %v", dbPath, err)
	}

	// 2. AHORA INICIAR RESTO DE INFRAESTRUCTURA
	if err := memory.StartFlightServerWithInstance(server, socketPath, natsURL); err != nil {
		log.Fatalf("[L1-MEMORY] Server Failure: %v", err)
	}
}
