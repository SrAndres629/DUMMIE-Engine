package orchestrator

import (
	"context"
	"encoding/json"
	"fmt"
	"net"
	"os"
	"os/signal"
	"path/filepath"
	"sync"
	"syscall"
	"time"
)

// Daemon representa el proceso de orquestación continua
type Daemon struct {
	Graph *StateGraph
	Store *StateStore
	Tasks chan *State
	Mu    sync.RWMutex
	Stop  chan struct{}

	InFlight   map[string]bool
	InFlightMu sync.Mutex
	socketPath string
}

func NewDaemon(g *StateGraph, s *StateStore) *Daemon {
	return &Daemon{
		Graph:    g,
		Store:    s,
		Tasks:    make(chan *State, 100),
		Stop:     make(chan struct{}),
		InFlight: make(map[string]bool),
	}
}

// Start inicia el loop reactivo del daemon
func (d *Daemon) Start(ctx context.Context) error {
	fmt.Println("[DAEMON] Iniciando motor de orquestación continua...")
	
	// Setup cleanup on exit
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
	go func() {
		select {
		case <-sigChan:
			d.Cleanup()
			os.Exit(0)
		case <-ctx.Done():
			d.Cleanup()
		}
	}()

	// Recuperar estados previos de la DB
	states, err := d.Store.LoadAll()
	if err == nil {
		for _, s := range states {
			if s.Status == "BLOCKED_WAITING_HUMAN" {
				fmt.Printf("[DAEMON] Recuperada rama suspendida: %s (%s)\n", s.ID, s.Goal)
			} else if s.Status != "SUCCESS" {
				d.Tasks <- s
			}
		}
	}

	go d.schedulerLoop(ctx)
	
	return d.startControlInterface(ctx)
}

func (d *Daemon) schedulerLoop(ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			return
		case <-d.Stop:
			return
		case task := <-d.Tasks:
			d.InFlightMu.Lock()
			if d.InFlight[task.ID] {
				fmt.Printf("[DAEMON] Tarea %s ya está en ejecución, omitiendo duplicado.\n", task.ID)
				d.InFlightMu.Unlock()
				continue
			}
			d.InFlight[task.ID] = true
			d.InFlightMu.Unlock()

			fmt.Printf("[DAEMON] Procesando tarea: %s -> %s\n", task.ID, task.Goal)
			go func(s *State) {
				defer func() {
					d.InFlightMu.Lock()
					delete(d.InFlight, s.ID)
					d.InFlightMu.Unlock()
				}()

				_, err := d.Graph.Run(ctx, s, s.Branch)
				if err != nil {
					fmt.Printf("[DAEMON] Error en tarea %s: %v\n", s.ID, err)
				}
			}(task)
		}
	}
}

func (d *Daemon) startControlInterface(ctx context.Context) error {
	d.socketPath = filepath.Join(os.Getenv("DUMMIE_AIWG_DIR"), "sockets", "dummied.sock")
	if os.Getenv("DUMMIE_AIWG_DIR") == "" {
		if pwd, err := os.Getwd(); err == nil {
			d.socketPath = filepath.Join(pwd, ".aiwg", "sockets", "dummied.sock")
		} else {
			d.socketPath = "/tmp/dummied.sock"
		}
	}

	// Asegurar existencia del directorio padre
	os.MkdirAll(filepath.Dir(d.socketPath), 0755)
	os.Remove(d.socketPath)
	l, err := net.Listen("unix", d.socketPath)
	if err != nil {
		return err
	}
	defer l.Close()

	fmt.Printf("[DAEMON] Interfaz de control activa en %s\n", d.socketPath)

	for {
		conn, err := l.Accept()
		if err != nil {
			select {
			case <-ctx.Done():
				return nil
			default:
				continue
			}
		}
		go d.handleControlConn(conn)
	}
}

type ControlCommand struct {
	Type     string         `json:"type"`
	Manifest *SwarmManifest `json:"manifest,omitempty"`
	Goal     string         `json:"goal,omitempty"`
	ID       string         `json:"id,omitempty"`
}

func (d *Daemon) handleControlConn(conn net.Conn) {
	defer conn.Close()

	var cmd ControlCommand
	if err := json.NewDecoder(conn).Decode(&cmd); err != nil {
		fmt.Fprintf(conn, `{"status": "error", "message": "invalid json: %v"}`+"\n", err)
		return
	}

	switch cmd.Type {
	case "SPAWN_SWARM":
		if cmd.Manifest == nil {
			fmt.Fprintln(conn, `{"status": "error", "message": "manifest is required for SPAWN_SWARM"}`)
			return
		}

		// Reconfigurar el grafo según el manifiesto
		// [AUTOPOIESIS] En el futuro, cada tarea podría tener su propio grafo inyectado en el State
		if err := d.Graph.BuildFromManifest(cmd.Manifest); err != nil {
			fmt.Fprintf(conn, `{"status": "error", "message": "failed to build graph: %v"}`+"\n", err)
			return
		}

		id := cmd.ID
		if id == "" {
			id = fmt.Sprintf("swarm_%d", time.Now().Unix())
		}

		state := &State{
			ID:     id,
			Goal:   cmd.Goal,
			Status: "PENDING",
			Branch: cmd.Manifest.Graph.Nodes[0].ID, // Iniciar en el primer nodo definido
		}

		d.Tasks <- state
		fmt.Fprintf(conn, `{"status": "ok", "task_id": "%s"}`+"\n", id)

	case "PING":
		fmt.Fprintln(conn, `{"status": "ok", "message": "PONG"}`)

	default:
		fmt.Fprintf(conn, `{"status": "error", "message": "unknown command: %s"}`+"\n", cmd.Type)
	}
}

func (d *Daemon) Cleanup() {
	fmt.Println("[DAEMON] Ejecutando limpieza antes del cierre...")
	if d.socketPath != "" {
		os.Remove(d.socketPath)
	}
}
