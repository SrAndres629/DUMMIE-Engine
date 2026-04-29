package main

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"os"
	"os/signal"
	"path/filepath"
	"syscall"

	"io.dummie.v2/overseer/internal/orchestrator"
)

func main() {
	fmt.Fprintln(os.Stderr, "=== DUMMIE SOVEREIGN DAEMON (dummied) ===")

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
		fmt.Fprintf(os.Stderr, "\n[DAEMON] Señal recibida (%v). Cerrando de forma controlada...\n", sig)
		cancel()
		os.Exit(0)
	}()

	// 4. Start Port Interface only when explicitly requested by a port supervisor.
	if shouldStartPortInterface() {
		go startPortInterface(ctx, daemon)
	}

	// 5. Start
	if err := daemon.Start(ctx); err != nil {
		log.Fatalf("Fallo crítico en el daemon: %v", err)
	}
}

func shouldStartPortInterface() bool {
	mode := os.Getenv("DUMMIE_PORT_INTERFACE")
	return mode == "stdio" || mode == "1"
}

type PortCommand struct {
	ID      string          `json:"id"`
	Command string          `json:"command"`
	Args    json.RawMessage `json:"args"`
}

type PortResponse struct {
	ID      string      `json:"id"`
	Status  string      `json:"status"`
	Payload interface{} `json:"payload"`
}

func startPortInterface(ctx context.Context, d *orchestrator.Daemon) {
	reader := bufio.NewReader(os.Stdin)
	for {
		select {
		case <-ctx.Done():
			return
		default:
			line, err := reader.ReadString('\n')
			if err != nil {
				if err == io.EOF {
					fmt.Fprintln(os.Stderr, "[DAEMON] STDIN cerrado (EOF). Apagando...")
					os.Exit(0)
				}
				fmt.Fprintf(os.Stderr, "[DAEMON] Error leyendo STDIN: %v\n", err)
				continue
			}

			processPortCommand(line, d)
		}
	}
}

func processPortCommand(line string, d *orchestrator.Daemon) {
	var cmd PortCommand
	if err := json.Unmarshal([]byte(line), &cmd); err != nil {
		sendPortResponse(cmd.ID, "error", map[string]string{"error": err.Error()})
		return
	}

	switch cmd.Command {
	case "ping":
		sendPortResponse(cmd.ID, "ok", map[string]bool{"pong": true})
	case "shutdown":
		sendPortResponse(cmd.ID, "ok", map[string]string{"status": "stopping"})
		os.Exit(0)
	default:
		sendPortResponse(cmd.ID, "error", map[string]string{"error": "unknown command"})
	}
}

func sendPortResponse(id, status string, payload interface{}) {
	resp := PortResponse{
		ID:      id,
		Status:  status,
		Payload: payload,
	}
	data, _ := json.Marshal(resp)
	fmt.Println(string(data))
}
