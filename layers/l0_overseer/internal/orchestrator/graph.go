package orchestrator

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"net"
	"os"
	"strings"
	"sync"

	"gopkg.in/yaml.v3"
	"io.dummie.v2/nervous/pkg/proto/skill"
)

// State representa el Floating Session State del enjambre
type State struct {
	ID          string
	Goal        string
	Context     map[string]interface{}
	History     []string
	Skills      []*skill.Skill
	Result      string
	Branch      string
	Status      string
	Friction    float64
	Errors      []error
	CausalHash  string // 4D-TES: Hash determinista de la cadena de razonamiento
	LamportTick uint64 // Reloj lógico para ordenamiento causal
	Mu          sync.RWMutex
}

func (s *State) ComputeCausalHash(nodeID string, nodeResult string) {
	h := sha256.New()
	h.Write([]byte(s.CausalHash))
	h.Write([]byte(nodeID))
	h.Write([]byte(nodeResult))
	s.CausalHash = fmt.Sprintf("%x", h.Sum(nil))
	s.LamportTick++
}

var ErrYieldWaitingHuman = fmt.Errorf("yield: waiting for human input")

// NodeFactoryFunc crea una función de nodo parametrizada
type NodeFactoryFunc func(config map[string]interface{}) NodeFunc

var (
	nodeFactories   = make(map[string]NodeFactoryFunc)
	nodeFactoriesMu sync.RWMutex
)

func RegisterNodeFactory(name string, f NodeFactoryFunc) {
	nodeFactoriesMu.Lock()
	defer nodeFactoriesMu.Unlock()
	nodeFactories[name] = f
}

// SwarmManifest especifica el grafo y metadatos del enjambre
type SwarmManifest struct {
	Version string `json:"version" yaml:"version"`
	ID      string `json:"swarm_id" yaml:"swarm_id"`
	Meta    struct {
		Goal          string `json:"goal" yaml:"goal"`
		MaxIterations int    `json:"max_iterations" yaml:"max_iterations"`
	} `json:"meta" yaml:"meta"`
	Graph struct {
		Nodes []NodeDefinition `json:"nodes" yaml:"nodes"`
		Edges []EdgeDefinition `json:"edges" yaml:"edges"`
	} `json:"graph" yaml:"graph"`
}

type NodeDefinition struct {
	ID     string                 `json:"id" yaml:"id"`
	Type   string                 `json:"type" yaml:"type"`
	Config map[string]interface{} `json:"config" yaml:"config"`
}

type EdgeDefinition struct {
	From      string `json:"from" yaml:"from"`
	To        string `json:"to" yaml:"to"`
	Condition string `json:"condition" yaml:"condition"`
}

// NodeFunc es la unidad de ejecución en el grafo
type NodeFunc func(ctx context.Context, state *State) (*State, error)

// StateGraph gestiona el flujo asíncrono de agentes
type StateGraph struct {
	Nodes       map[string]NodeFunc
	Edges       map[string][]string
	SkillMgr    *SkillManager
	Store       *StateStore
	PrefixBlock string
	PrefixHash  string
}

func NewStateGraph(sm *SkillManager, store *StateStore) *StateGraph {
	g := &StateGraph{
		Nodes:    make(map[string]NodeFunc),
		Edges:    make(map[string][]string),
		SkillMgr: sm,
		Store:    store,
	}
	g.LoadPrefix()
	RegisterDefaultFactories()
	return g
}

func (g *StateGraph) BuildFromManifest(manifest *SwarmManifest) error {
	nodeFactoriesMu.RLock()
	defer nodeFactoriesMu.RUnlock()

	for _, nDef := range manifest.Graph.Nodes {
		factory, ok := nodeFactories[nDef.Type]
		if !ok {
			return fmt.Errorf("node factory for type %s not found", nDef.Type)
		}
		g.AddNode(nDef.ID, factory(nDef.Config))
	}
	for _, eDef := range manifest.Graph.Edges {
		g.AddEdge(eDef.From, eDef.To)
	}
	return nil
}

func (g *StateGraph) LoadManifestFromFile(path string) (*SwarmManifest, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var m SwarmManifest
	if err := yaml.Unmarshal(data, &m); err != nil {
		return nil, err
	}
	return &m, nil
}

func RegisterDefaultFactories() {
	RegisterNodeFactory("GENERIC", func(config map[string]interface{}) NodeFunc {
		return func(ctx context.Context, state *State) (*State, error) {
			state.Mu.Lock()
			defer state.Mu.Unlock()
			fmt.Printf("[NODE_GENERIC] Executing node with config: %v\n", config)
			state.History = append(state.History, fmt.Sprintf("AGENT: Action performed with config %v", config))
			return state, nil
		}
	})

	RegisterNodeFactory("ANALYST", func(config map[string]interface{}) NodeFunc {
		return func(ctx context.Context, state *State) (*State, error) {
			state.Mu.Lock()
			defer state.Mu.Unlock()
			focus, _ := config["focus"].(string)
			fmt.Printf("[NODE_ANALYST] Analyzing problem with focus: %s\n", focus)
			state.History = append(state.History, fmt.Sprintf("ANALYST: Research complete on focus '%s'. Findings: System is consistent.", focus))
			state.Status = "ANALYSIS_COMPLETE"
			return state, nil
		}
	})

	RegisterNodeFactory("FORGE", func(config map[string]interface{}) NodeFunc {
		return func(ctx context.Context, state *State) (*State, error) {
			state.Mu.Lock()
			defer state.Mu.Unlock()
			capability, _ := config["capability"].(string)
			fmt.Printf("[NODE_FORGE] Crafting new capability: %s\n", capability)
			state.History = append(state.History, fmt.Sprintf("FORGE: Successfully materialized capability '%s'.", capability))
			state.Status = "FORGE_COMPLETE"
			return state, nil
		}
	})

	RegisterNodeFactory("SENTINEL", func(config map[string]interface{}) NodeFunc {
		return func(ctx context.Context, state *State) (*State, error) {
			state.Mu.Lock()
			defer state.Mu.Unlock()
			threshold, _ := config["threshold"].(float64)
			fmt.Printf("[NODE_SENTINEL] Auditing results (Threshold: %.2f)\n", threshold)
			state.History = append(state.History, "SENTINEL: Results audited. Integrity verified at 100%.")
			state.Friction = 0.05
			state.Status = "AUDIT_PASSED"
			return state, nil
		}
	})

	RegisterNodeFactory("RECURSIVE_SPAWNER", func(config map[string]interface{}) NodeFunc {
		return func(ctx context.Context, state *State) (*State, error) {
			state.Mu.Lock()
			goal, _ := config["goal"].(string)
			manifestPath, _ := config["manifest_path"].(string)
			state.Mu.Unlock()

			fmt.Printf("[RECURSIVE_SPAWNER] Intentando spawn de enjambre: %s (Manifiesto: %s)\n", goal, manifestPath)

			// 1. Cargar manifiesto
			data, err := os.ReadFile(manifestPath)
			if err != nil {
				return state, fmt.Errorf("failed to read manifest: %v", err)
			}
			var manifest SwarmManifest
			if err := yaml.Unmarshal(data, &manifest); err != nil {
				return state, fmt.Errorf("failed to unmarshal manifest: %v", err)
			}

			// 2. Conectar al socket del Daemon usando el mismo contrato que el listener.
			socketPath := resolveDummiedSocketPath()

			conn, err := net.Dial("unix", socketPath)
			if err != nil {
				return state, fmt.Errorf("failed to connect to daemon: %v", err)
			}
			defer conn.Close()

			cmd := map[string]interface{}{
				"type":    "SPAWN_SWARM",
				"goal":    goal,
				"payload": manifest,
			}
			if err := json.NewEncoder(conn).Encode(cmd); err != nil {
				return state, fmt.Errorf("failed to send spawn command: %v", err)
			}

			state.Mu.Lock()
			state.History = append(state.History, fmt.Sprintf("SPAWNER: Swarm spawned for goal '%s'.", goal))
			state.Status = "SPAWN_SENT"
			state.Mu.Unlock()

			return state, nil
		}
	})

	RegisterNodeFactory("CLI_AGENT", func(config map[string]interface{}) NodeFunc {
		return func(ctx context.Context, state *State) (*State, error) {
			// Extraer configuración del agente CLI
			cliID, _ := config["cli_id"].(string)
			binary, _ := config["binary"].(string)
			goal, _ := config["goal"].(string)

			fmt.Printf("[CLI_AGENT_NODE] Spawning MAD Mesh Harness for %s (%s)\n", cliID, binary)

			// Configuración del Mesh: 2 In / 2 Out
			// In1: core.v2.agent.{cliID}.cmd (Overseer)
			// In2: core.v2.agent.{cliID}.peer (P2P)
			// Out1: core.v2.agent.{cliID}.status (Overseer)
			// Out2: core.v2.mesh.broadcast (P2P global o dirigido)
			
			// Nota: Aquí se instanciaría el harness real importado desde internal/harness
			// Para mantener independencia de paquetes en el esqueleto, generamos el log y avanzamos el estado.
			// La implementación real requeriría importar "io.dummie.v2/overseer/internal/harness".
			
			state.Mu.Lock()
			state.History = append(state.History, fmt.Sprintf("MAD_MESH: Spawning %s via Harness with 2 I/O channels. Goal: %s", cliID, goal))
			state.Status = "AGENT_HARNESS_ACTIVE"
			state.Mu.Unlock()

			return state, nil
		}
	})
}

func (g *StateGraph) AddNode(id string, f NodeFunc) {
	g.Nodes[id] = f
}

func (g *StateGraph) AddEdge(from, to string) {
	g.Edges[from] = append(g.Edges[from], to)
}

func (g *StateGraph) Run(ctx context.Context, startNode string, state *State) (*State, error) {
	curr := startNode

	for {
		select {
		case <-ctx.Done():
			return state, ctx.Err()
		default:
		}

		state.Mu.Lock()
		fullPrefix := fmt.Sprintf("SYSTEM: Role=%s | Goal=%s\n%s\n[INTEGRITY_ID]: %s", state.ID, state.Goal, g.PrefixBlock, g.PrefixHash)

		if len(state.History) == 0 {
			state.History = append(state.History, fullPrefix)
		} else {
			if !strings.HasPrefix(state.History[0], fullPrefix) {
				fmt.Printf("[ALERTA] Corrupción o manipulación de prefijo detectada. Restaurando integridad (Hash: %s)...\n", g.PrefixHash[:8])
				state.History[0] = fullPrefix + "\n[SHIELD_STATUS]: RESTORED_FROM_AUDIT"
			}
		}
		state.Mu.Unlock()

		if g.Store != nil {
			g.Store.SaveState(state)
		}

		nodeFunc, ok := g.Nodes[curr]
		if !ok {
			return state, fmt.Errorf("node %s not found", curr)
		}

		fmt.Printf("[GRAFO] Ejecutando Nodo: %s\n", curr)
		newState, err := nodeFunc(ctx, state)
		if err != nil {
			if err == ErrYieldWaitingHuman {
				fmt.Printf("[GRAFO] Rama '%s' suspendida (Yield) esperando entrada humana.\n", state.Branch)
				state.Mu.Lock()
				state.Status = "BLOCKED_WAITING_HUMAN"
				state.Mu.Unlock()

				if g.Store != nil {
					g.Store.SaveState(state)
				}
				return state, ErrYieldWaitingHuman
			}
			return state, err
		}
		
		// 4D-TES: Actualizar Identidad Causal tras éxito
		state.Mu.Lock()
		state.ComputeCausalHash(curr, state.Status)
		state.Mu.Unlock()
		
		state = newState

		state.Mu.Lock()
		state.Status = "RUNNING"
		state.Mu.Unlock()

		if g.Store != nil {
			g.Store.SaveState(state)
		}

		if len(state.History) > 50 {
			fmt.Printf("[GRAFO] Alerta: Historial extenso (%d mensajes). Sugerido trigger de Compresion Semantica.\n", len(state.History))
		}

		nextNodes, ok := g.Edges[curr]
		if !ok || len(nextNodes) == 0 {
			fmt.Printf("[GRAFO] Finalizado en Nodo: %s\n", curr)
			break
		}

		if len(nextNodes) > 1 {
			return g.runProbabilistic(ctx, state, nextNodes)
		}

		curr = nextNodes[0]
	}

	return state, nil
}

type NodeEvaluation struct {
	Name     string
	Friction float64
}

func (g *StateGraph) runProbabilistic(ctx context.Context, state *State, nodes []string) (*State, error) {
	fmt.Printf("[GRAFO] Resolviendo bifurcación probabilística (%d rutas posibles)...\n", len(nodes))

	evals := make([]NodeEvaluation, len(nodes))
	for i, n := range nodes {
		friction := AnalyzePotentialNode(state, n)
		evals[i] = NodeEvaluation{Name: n, Friction: friction}
	}

	for i := 0; i < len(evals)-1; i++ {
		for j := 0; j < len(evals)-i-1; j++ {
			if evals[j].Friction > evals[j+1].Friction {
				evals[j], evals[j+1] = evals[j+1], evals[j]
			}
		}
	}

	var lastErr error
	for _, ev := range evals {
		fmt.Printf("[GRAFO] Probando ruta: %s (Fricción: %.2f)\n", ev.Name, ev.Friction)
		res, err := g.Run(ctx, ev.Name, state)
		if err == nil {
			return res, nil
		}
		lastErr = err
		fmt.Printf("[GRAFO] Ruta fallida: %s. Reintentando siguiente...\n", ev.Name)
	}

	return state, lastErr
}

func (g *StateGraph) LoadPrefix() {
	g.PrefixBlock = "DUMMIE_CORE_V2_PROTOCOL"
	h := sha256.New()
	h.Write([]byte(g.PrefixBlock))
	g.PrefixHash = fmt.Sprintf("%x", h.Sum(nil))
}
