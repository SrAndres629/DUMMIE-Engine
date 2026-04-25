package orchestrator

import (
	"context"
	"crypto/sha256"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"

	"io.dummie.v2/nervous/pkg/proto/skill"
)

// State representa el Floating Session State del enjambre
type State struct {
	ID      string
	Goal    string
	Context map[string]interface{}
	History []string
	Skills  []*skill.Skill
	Result   string
	Branch   string
	Status   string
	Friction float64
	Errors   []error
	Mu       sync.RWMutex
}

var ErrYieldWaitingHuman = fmt.Errorf("yield: waiting for human input")


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
	return g
}

func (g *StateGraph) LoadPrefix() {
	identity, _ := readRepoControlFile("IDENTITY.md")
	rules, _ := readRepoControlFile("GEMINI.md")

	g.PrefixBlock = fmt.Sprintf("=== SOVEREIGN IDENTITY ===\n%s\n\n=== ARCHITECTURAL RULES ===\n%s\n",
		string(identity), string(rules))

	h := sha256.New()
	h.Write([]byte(g.PrefixBlock))
	g.PrefixHash = fmt.Sprintf("%x", h.Sum(nil))
}

func readRepoControlFile(name string) ([]byte, error) {
	candidates := make([]string, 0, 8)
	if root := os.Getenv("DUMMIE_ROOT_DIR"); root != "" {
		candidates = append(candidates, filepath.Join(root, name))
	}
	candidates = append(candidates,
		name,
		filepath.Join("..", name),
		filepath.Join("..", "..", name),
		filepath.Join("..", "..", "..", name),
		filepath.Join("..", "..", "..", "..", name),
	)

	for _, path := range candidates {
		data, err := os.ReadFile(path)
		if err == nil {
			return data, nil
		}
	}
	return []byte{}, fmt.Errorf("control file not found: %s", name)
}

func (g *StateGraph) AddNode(name string, f NodeFunc) {
	g.Nodes[name] = f
}

func (g *StateGraph) AddEdge(from, to string) {
	g.Edges[from] = append(g.Edges[from], to)
}

// Run ejecuta el grafo desde un node inicial
func (g *StateGraph) Run(ctx context.Context, initialState *State, startNode string) (*State, error) {
	curr := startNode
	state := initialState

	for {
		// [STABLE PREFIX] Hardened Prefix: Identity + Golden Rules (File-based)
		state.Mu.Lock()
		fullPrefix := fmt.Sprintf("SYSTEM: Role=%s | Goal=%s\n%s\n[INTEGRITY_ID]: %s", state.ID, state.Goal, g.PrefixBlock, g.PrefixHash)

		if len(state.History) == 0 {
			state.History = append(state.History, fullPrefix)
		} else {
			// [HARDENING] Validar integridad del bloque completo esperado (no solo substring/hash).
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
				
				// Rompemos el ciclo sin devolver error fatal para que el orquestador global siga
				return state, nil
			}
			return state, err
		}
		state = newState

		state.Mu.Lock()
		state.Status = "RUNNING"
		state.Mu.Unlock()
		
		if g.Store != nil {
			g.Store.SaveState(state)
		}

		// [COMPRESSION CHECK] Si el historial es muy largo, se sugiere llamar al utility_compressor
		if len(state.History) > 50 {
			fmt.Printf("[GRAFO] Alerta: Historial extenso (%d mensajes). Sugerido trigger de Compresion Semantica.\n", len(state.History))
		}

		// Determinar siguiente nodo (lógica simple por ahora)
		nextNodes, ok := g.Edges[curr]
		if !ok || len(nextNodes) == 0 {
			fmt.Printf("[GRAFO] Finalizado en Nodo: %s\n", curr)
			break
		}

	// Si hay múltiples nodos, lanzamos el "Fan-out" probabilístico
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

	// Ordenar burbuja simple (de menor a mayor fricción)
	for i := 0; i < len(evals)-1; i++ {
		for j := 0; j < len(evals)-i-1; j++ {
			if evals[j].Friction > evals[j+1].Friction {
				evals[j], evals[j+1] = evals[j+1], evals[j]
			}
		}
	}

	var lastErr error
	var lastYieldedState *State

	// Ejecutar secuencialmente priorizando menor fricción
	for _, eval := range evals {
		fmt.Printf("[GRAFO] Intentando ruta '%s' (Fricción estimada: %.2f)\n", eval.Name, eval.Friction)
		
		// [BRANCH ISOLATION 2.0] Clonar estado y aplicar TurboQuant
		clonedState := g.cloneState(state)

		clonedState.Mu.Lock()
		if len(clonedState.History) > 10 {
			prefix := clonedState.History[0]
			recent := clonedState.History[len(clonedState.History)-3:]
			clonedState.History = append([]string{prefix, "[BRANCH_SUMMARY]: Historial previo podado por TurboQuant."}, recent...)
		}
		clonedState.Branch = eval.Name
		clonedState.Mu.Unlock()

		res, err := g.Run(ctx, clonedState, eval.Name)
		if err != nil {
			fmt.Printf("[GRAFO] Ruta '%s' falló con error: %v. Buscando alternativa...\n", eval.Name, err)
			lastErr = err
			continue // Probar siguiente ruta
		}

		res.Mu.RLock()
		status := res.Status
		res.Mu.RUnlock()

		if status == "BLOCKED_WAITING_HUMAN" {
			fmt.Printf("[GRAFO] Ruta '%s' bloqueada (Yield). Buscando alternativa...\n", eval.Name)
			lastYieldedState = res
			continue // Probar siguiente ruta
		}

		// Éxito total sin bloqueos
		fmt.Printf("[GRAFO] Ruta '%s' completada con éxito. Descartando otras opciones.\n", eval.Name)
		state.Mu.Lock()
		state.Result = res.Result
		state.History = res.History
		state.Context = res.Context
		state.Errors = res.Errors
		state.Status = res.Status
		state.Friction = eval.Friction
		state.Mu.Unlock()
		return state, nil
	}

	// Si todas fallaron o hicieron yield
	if lastYieldedState != nil {
		fmt.Println("[GRAFO] Todas las rutas fallaron o están bloqueadas. Retornando estado Yield.")
		state.Mu.Lock()
		state.Result = lastYieldedState.Result
		state.History = lastYieldedState.History
		state.Context = lastYieldedState.Context
		state.Errors = lastYieldedState.Errors
		state.Status = "BLOCKED_WAITING_HUMAN"
		state.Mu.Unlock()
		return state, nil
	}

	return state, fmt.Errorf("probabilistic execution failed all routes: %v", lastErr)
}


func (g *StateGraph) cloneState(s *State) *State {
	s.Mu.RLock()
	defer s.Mu.RUnlock()

	newCtx := make(map[string]interface{})
	for k, v := range s.Context {
		newCtx[k] = v
	}

	return &State{
		ID:      s.ID,
		Goal:    s.Goal,
		Context: newCtx,
		History: append([]string{}, s.History...),
		Skills:  append([]*skill.Skill{}, s.Skills...),
		Branch:  s.Branch,
	}
}
