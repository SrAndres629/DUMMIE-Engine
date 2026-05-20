package harness

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"os/exec"
	"sync"
	"time"

	"github.com/nats-io/nats.go"
)

// AgentContext define el estado que se inyectará en el CLI
type AgentContext struct {
	SessionID   string            `json:"session_id"`
	Goal        string            `json:"goal"`
	SystemPrompt string           `json:"system_prompt"`
	Skills      []string          `json:"skills"`
	Authority   string            `json:"authority"`
	MeshConfig  MeshConfig        `json:"mesh_config"`
}

// MeshConfig define las 2 entradas y 2 salidas P2P del agente
type MeshConfig struct {
	InCommandSubject  string `json:"in_command_subject"` // Entrada 1: Control (Overseer)
	InPeerSubject     string `json:"in_peer_subject"`    // Entrada 2: P2P (Agent to Agent)
	OutStatusSubject  string `json:"out_status_subject"` // Salida 1: Control (Overseer)
	OutPeerSubject    string `json:"out_peer_subject"`   // Salida 2: P2P (Agent to Agent)
}

// CliHarness envuelve un CLI (Gemini, Codex, OpenCode) conectándolo al Mesh
type CliHarness struct {
	ID        string
	Binary    string
	Context   AgentContext
	nc        *nats.Conn
	cmd       *exec.Cmd
	stdin     io.WriteCloser
	stdout    io.ReadCloser
	stderr    io.ReadCloser
	ctx       context.Context
	cancel    context.CancelFunc
	wg        sync.WaitGroup
}

func NewCliHarness(id, binary string, natsURL string, ctxData AgentContext) (*CliHarness, error) {
	nc, err := nats.Connect(natsURL)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to NATS mesh: %v", err)
	}

	ctx, cancel := context.WithCancel(context.Background())

	return &CliHarness{
		ID:      id,
		Binary:  binary,
		Context: ctxData,
		nc:      nc,
		ctx:     ctx,
		cancel:  cancel,
	}, nil
}

func (h *CliHarness) Start() error {
	log.Printf("[HARNESS] Booting CLI Agent: %s (Binary: %s)", h.ID, h.Binary)

	h.cmd = exec.CommandContext(h.ctx, h.Binary)
	
	// Configurar Pipes (Las 2 Entradas y 2 Salidas de nivel OS)
	var err error
	h.stdin, err = h.cmd.StdinPipe()
	if err != nil { return err }
	
	h.stdout, err = h.cmd.StdoutPipe()
	if err != nil { return err }

	h.stderr, err = h.cmd.StderrPipe()
	if err != nil { return err }

	if err := h.cmd.Start(); err != nil {
		return fmt.Errorf("failed to start CLI process: %v", err)
	}

	h.wg.Add(2)
	go h.pumpStdoutToStatus()
	go h.listenMesh()

	// Inyectar contexto inicial (Prompts, Skills)
	h.injectContext()

	return nil
}

func (h *CliHarness) injectContext() {
	// MANDATO SOBERANO: Forzar la habilidad de auto-cristalización y colaboración
	hasAutoCrystallize := false
	for _, skill := range h.Context.Skills {
		if skill == "auto_crystallize" {
			hasAutoCrystallize = true
			break
		}
	}
	if !hasAutoCrystallize {
		h.Context.Skills = append(h.Context.Skills, "auto_crystallize")
	}

	payload, _ := json.Marshal(h.Context)
	msg := fmt.Sprintf("[SYSTEM_INJECTION]\n%s\n[END_INJECTION]\n", payload)
	h.stdin.Write([]byte(msg))
	log.Printf("[HARNESS] Context injected for %s (includes auto_crystallize)", h.ID)
}

// listenMesh conecta las Entradas P2P y Control al Stdin del CLI
func (h *CliHarness) listenMesh() {
	defer h.wg.Done()

	// Entrada 1: Control (Overseer -> CLI)
	subCmd, err := h.nc.SubscribeSync(h.Context.MeshConfig.InCommandSubject)
	if err != nil {
		log.Printf("[HARNESS] Error subscribing to command mesh: %v", err)
		return
	}

	// Entrada 2: P2P (Peer -> CLI)
	subPeer, err := h.nc.SubscribeSync(h.Context.MeshConfig.InPeerSubject)
	if err != nil {
		log.Printf("[HARNESS] Error subscribing to peer mesh: %v", err)
		return
	}

	for {
		select {
		case <-h.ctx.Done():
			return
		default:
			// Poll Command Stream
			msgCmd, err := subCmd.NextMsg(100 * time.Millisecond)
			if err == nil {
				h.stdin.Write([]byte(fmt.Sprintf("[OVERSEER_CMD]: %s\n", msgCmd.Data)))
			}

			// Poll Peer Stream
			msgPeer, err := subPeer.NextMsg(100 * time.Millisecond)
			if err == nil {
				h.stdin.Write([]byte(fmt.Sprintf("[PEER_MSG]: %s\n", msgPeer.Data)))
			}
		}
	}
}

// pumpStdoutToStatus conecta el Stdout del CLI a las Salidas P2P y Control
func (h *CliHarness) pumpStdoutToStatus() {
	defer h.wg.Done()
	scanner := bufio.NewScanner(h.stdout)
	
	for scanner.Scan() {
		text := scanner.Text()
		
		// Enrutamiento de salidas inteligente:
		// Si el CLI produce un comando @peer, va a la Salida 2 (P2P).
		// De lo contrario, va a la Salida 1 (Status).
		
		if len(text) > 6 && text[:6] == "@peer " {
			payload := fmt.Sprintf(`{"from": "%s", "msg": "%s"}`, h.ID, text[6:])
			h.nc.Publish(h.Context.MeshConfig.OutPeerSubject, []byte(payload))
			log.Printf("[HARNESS] P2P Broadcast from %s", h.ID)
		} else {
			h.nc.Publish(h.Context.MeshConfig.OutStatusSubject, []byte(text))
		}
	}
}

func (h *CliHarness) Stop() {
	log.Printf("[HARNESS] Shutting down agent %s", h.ID)
	h.cancel()
	if h.cmd != nil && h.cmd.Process != nil {
		h.cmd.Process.Kill()
	}
	h.nc.Close()
	h.wg.Wait()
}
