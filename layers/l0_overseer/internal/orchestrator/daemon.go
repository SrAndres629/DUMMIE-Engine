package orchestrator

import (
	"context"
	"fmt"
	"net"
	"os"
	"path/filepath"
	"sync"
)

// Daemon representa el proceso de orquestación continua
type Daemon struct {
	Graph *StateGraph
	Store *StateStore
	Tasks chan *State
	Mu    sync.RWMutex
	Stop  chan struct{}
}

func NewDaemon(g *StateGraph, s *StateStore) *Daemon {
	return &Daemon{
		Graph: g,
		Store: s,
		Tasks: make(chan *State, 100),
		Stop:  make(chan struct{}),
	}
}

// Start inicia el loop reactivo del daemon
func (d *Daemon) Start(ctx context.Context) error {
	fmt.Println("[DAEMON] Iniciando motor de orquestación continua...")
	
	// Recuperar estados previos de la DB
	states, err := d.Store.LoadAll()
	if err == nil {
		for _, s := range states {
			if s.Status == "BLOCKED_WAITING_HUMAN" {
				fmt.Printf("[DAEMON] Recuperada rama suspendida: %s (%s)\n", s.ID, s.Goal)
				// Estas no se meten al canal de Tasks automáticamente, esperan un WAKE
			} else if s.Status != "SUCCESS" {
				// Re-encolar tareas inacabadas
				d.Tasks <- s
			}
		}
	}

	// Loop de control
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
			fmt.Printf("[DAEMON] Procesando tarea: %s -> %s\n", task.ID, task.Goal)
			go func(s *State) {
				_, err := d.Graph.Run(ctx, s, s.Branch)
				if err != nil {
					fmt.Printf("[DAEMON] Error en tarea %s: %v\n", s.ID, err)
				}
			}(task)
		}
	}
}

func (d *Daemon) startControlInterface(ctx context.Context) error {
	socketPath := filepath.Join(os.Getenv("DUMMIE_AIWG_DIR"), "dummied.sock")
	if os.Getenv("DUMMIE_AIWG_DIR") == "" {
		socketPath = "/tmp/dummied.sock"
	}

	os.Remove(socketPath)
	l, err := net.Listen("unix", socketPath)
	if err != nil {
		return err
	}
	defer l.Close()

	fmt.Printf("[DAEMON] Interfaz de control activa en %s\n", socketPath)

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

func (d *Daemon) handleControlConn(conn net.Conn) {
	defer conn.Close()
	// Aquí implementaríamos el protocolo gRPC o un simple JSON-RPC
	// Por ahora mockeamos la recepción de un comando SPAWN
	fmt.Fprintln(conn, "DUMMIE Daemon Control v1.0")
}
