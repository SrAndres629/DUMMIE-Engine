package orchestrator

import (
	"context"
	"fmt"
	"sync"

	"io.dummie.v2/nervous/pkg/proto/skill"
)

// State representa el Floating Session State del enjambre
type State struct {
	ID        string
	Goal      string
	Context   map[string]interface{}
	History   []string
	Skills    []*skill.Skill
	Result    string
	Branch    string
	Errors    []error
	Mu        sync.RWMutex
}

// NodeFunc es la unidad de ejecución en el grafo
type NodeFunc func(ctx context.Context, state *State) (*State, error)

// StateGraph gestiona el flujo asíncrono de agentes
type StateGraph struct {
	Nodes        map[string]NodeFunc
	Edges        map[string][]string
	SkillMgr     *SkillManager
}

func NewStateGraph(sm *SkillManager) *StateGraph {
	return &StateGraph{
		Nodes:    make(map[string]NodeFunc),
		Edges:    make(map[string][]string),
		SkillMgr: sm,
	}
}

func (g *StateGraph) AddNode(name string, f NodeFunc) {
	g.Nodes[name] = f
}

func (g *StateGraph) AddEdge(from, to string) {
	g.Edges[from] = append(g.Edges[from], to)
}

// Run ejecuta el grafo desde un nodo inicial
func (g *StateGraph) Run(ctx context.Context, initialState *State, startNode string) (*State, error) {
	curr := startNode
	state := initialState

	for {
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
			// Clonar estado para cada rama (Quantum State Cloning)
			clonedState := g.cloneState(state)
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
