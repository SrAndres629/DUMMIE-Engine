package main

import (
	"log"
	"os"

	"io.dummie.v2/nervous/internal/memory"
)

func main() {
	dbPath := os.Getenv("KUZU_DB_PATH")
	if dbPath == "" {
		dbPath = os.ExpandEnv("$HOME/Escritorio/DUMMIE Engine/.aiwg/memory/kuzu")
	}
	
	socketPath := os.Getenv("MEMORY_SOCKET_PATH")
	if socketPath == "" {
		socketPath = "/tmp/dummie_memory.sock"
	}

	natsURL := os.Getenv("NATS_URL")
	if natsURL == "" {
		natsURL = "nats://localhost:4222"
	}

	log.Printf("[L1-MEMORY] Iniciando Memory Plane (Data Plane)...")
	log.Printf("[L1-MEMORY] DB: %s", dbPath)
	log.Printf("[L1-MEMORY] Socket: %s", socketPath)

	if err := memory.StartFlightServer(dbPath, socketPath, natsURL); err != nil {
		log.Fatalf("[L1-MEMORY] FATAL ERROR: %v", err)
	}
}
