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
	Result  string
	Branch  string
	Errors  []error
	Mu      sync.RWMutex
}

// NodeFunc es la unidad de ejecución en el grafo
type NodeFunc func(ctx context.Context, state *State) (*State, error)

// StateGraph gestiona el flujo asíncrono de agentes
type StateGraph struct {
	Nodes       map[string]NodeFunc
	Edges       map[string][]string
	SkillMgr    *SkillManager
	PrefixBlock string
	PrefixHash  string
}

func NewStateGraph(sm *SkillManager) *StateGraph {
	g := &StateGraph{
		Nodes:    make(map[string]NodeFunc),
		Edges:    make(map[string][]string),
		SkillMgr: sm,
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

		nodeFunc, ok := g.Nodes[curr]
		if !ok {
			return state, fmt.Errorf("node %s not found", curr)
		}

		fmt.Printf("[GRAFO] Ejecutando Nodo: %s\n", curr)
		newState, err := nodeFunc(ctx, state)
		if err != nil {
			return state, err
		}
		state = newState

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

		// Si hay múltiples nodos, lanzamos el "Fan-out" (Paralelismo Cuántico)
		if len(nextNodes) > 1 {
			return g.runParallel(ctx, state, nextNodes)
		}

		curr = nextNodes[0]
	}

	return state, nil
}

func (g *StateGraph) runParallel(ctx context.Context, state *State, nodes []string) (*State, error) {
	var wg sync.WaitGroup
	results := make(chan *State, len(nodes))
	errors := make(chan error, len(nodes))

	for _, n := range nodes {
		wg.Add(1)
		go func(nodeName string) {
			defer wg.Done()
			// [BRANCH ISOLATION 2.0] Clonar estado y aplicar TurboQuant (Truncado agresivo)
			clonedState := g.cloneState(state)

			clonedState.Mu.Lock()
			if len(clonedState.History) > 10 {
				// Mantener solo el prefijo (índice 0) y los últimos 3 mensajes para la rama
				prefix := clonedState.History[0]
				recent := clonedState.History[len(clonedState.History)-3:]
				clonedState.History = append([]string{prefix, "[BRANCH_SUMMARY]: Historial previo podado por TurboQuant."}, recent...)
			}
			clonedState.Branch = nodeName
			clonedState.Mu.Unlock()

			res, err := g.Run(ctx, clonedState, nodeName)
			if err != nil {
				errors <- err
				return
			}
			results <- res
		}(n)
	}

	wg.Wait()
	close(results)
	close(errors)

	// Lógica de Fusión (Merge) - Tomamos el primero exitoso y actualizamos el estado original
	select {
	case res := <-results:
		state.Mu.Lock()
		state.Result = res.Result
		state.History = res.History
		state.Context = res.Context
		state.Errors = res.Errors
		state.Mu.Unlock()
		return state, nil
	case err := <-errors:
		return state, err
	default:
		return state, fmt.Errorf("parallel execution failed with no results")
	}
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
