package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"path/filepath"
	"syscall"

	"io.dummie.v2/overseer/internal/orchestrator"
)

func main() {
	fmt.Println("=== DUMMIE SOVEREIGN DAEMON (dummied) ===")

	// 1. Setup Infra
	dbPath := filepath.Join(os.Getenv("DUMMIE_AIWG_DIR"), "memory", "state.db")
	if os.Getenv("DUMMIE_AIWG_DIR") == "" {
		dbPath = "memory/state.db"
	}

	store, err := orchestrator.NewStateStore(dbPath)
	if err != nil {
		log.Fatalf("Error inicializando Store: %v", err)
	}
	defer store.Close()

	sm := &orchestrator.SkillManager{}
	graph := orchestrator.NewStateGraph(sm, store)

	// 2. Setup Daemon
	daemon := orchestrator.NewDaemon(graph, store)

	// 3. Context & Signals
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		sig := <-sigChan
		fmt.Printf("\n[DAEMON] Señal recibida (%v). Cerrando de forma controlada...\n", sig)
		cancel()
		os.Exit(0)
	}()

	// 4. Start
	if err := daemon.Start(ctx); err != nil {
		log.Fatalf("Fallo crítico en el daemon: %v", err)
	}
}
