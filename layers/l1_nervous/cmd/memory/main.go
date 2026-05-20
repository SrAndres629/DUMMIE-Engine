package main

import (
	"log"
	"os"
	"path/filepath"

	"github.com/nats-io/nats.go"
	"io.dummie.v2/nervous/internal/memory"
)

func main() {
	// 0. DETERMINISMO DE RUTAS
	execPath, _ := os.Executable()
	baseDir := filepath.Dir(filepath.Dir(filepath.Dir(execPath))) // layers/l1_nervous/cmd/memory -> layers/l1_nervous
	
	aiwgDir := os.Getenv("DUMMIE_AIWG_DIR")
	if aiwgDir == "" {
		aiwgDir = filepath.Join(baseDir, "..", "..", ".aiwg")
	}
	absAiwg, _ := filepath.Abs(aiwgDir)

	dbPath := os.Getenv("DUMMIE_KUZU_DB_PATH")
	if dbPath == "" {
		dbPath = filepath.Join(absAiwg, "memory", "loci.db")
	}

	socketPath := os.Getenv("MEMORY_SOCKET_PATH")
	if socketPath == "" {
		socketPath = filepath.Join(absAiwg, "sockets", "flight.sock")
	}

	natsURL := os.Getenv("NATS_URL")
	if natsURL == "" {
		natsURL = nats.DefaultURL
	}

	log.Printf("[L1-MEMORY] Palacio de Loci - Iniciando Data Plane...")
	log.Printf("[L1-MEMORY] SSoT AIWG: %s", absAiwg)
	log.Printf("[L1-MEMORY] DB (Kuzu): %s", dbPath)
	log.Printf("[L1-MEMORY] Flight Socket: %s", socketPath)

	// 1. ABRIR KUZU PRIMERO (Aislamiento de Lock)
	if err := memory.ResolveStaleLocks(dbPath); err != nil {
		log.Printf("[L1-MEMORY] WARNING: Stale lock recovery attempted: %v", err)
	}

	// 2. CONECTAR NATS (Control Plane)
	nc, err := nats.Connect(natsURL)
	if err != nil {
		log.Printf("[L1-MEMORY] WARNING: NATS unavailable at %s. Operating in DEGRADED mode (no telemetry).", natsURL)
	} else {
		defer nc.Close()
		log.Printf("[L1-MEMORY] NATS Connected.")
	}

	server, err := memory.NewDummieMemoryServer(dbPath, nc)
	if err != nil {
		log.Fatalf("[L1-MEMORY] CRITICAL: Failed to open KuzuDB: %v", err)
	}

	// 3. INICIAR SERVIDOR FLIGHT (Arrow IPC)
	if err := memory.StartFlightServerWithInstance(server, socketPath, natsURL); err != nil {
		log.Fatalf("[L1-MEMORY] SERVER SHUTDOWN: %v", err)
	}
}
