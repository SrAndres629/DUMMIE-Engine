package orchestrator

import (
	"fmt"
	"strings"
)

// Evaluator define la interfaz para calcular la fricción de un estado
type Evaluator interface {
	EvaluateFriction(state *State) float64
}

// HeuristicEvaluator es una implementación básica del MCTS Friction Score
type HeuristicEvaluator struct{}

// EvaluateFriction analiza el estado y le asigna un puntaje de fricción.
// Menor fricción (0.0) = Alta probabilidad de éxito.
// Mayor fricción = Rama bloqueada o inestable.
func (e *HeuristicEvaluator) EvaluateFriction(state *State) float64 {
	state.Mu.RLock()
	defer state.Mu.RUnlock()

	friction := 1.0 // Base score

	// 1. Penalización por errores acumulados
	friction += float64(len(state.Errors)) * 0.5

	// 2. Penalización drástica si la rama está en espera (Yield)
	if state.Status == "BLOCKED_WAITING_HUMAN" {
		friction += 100.0 // Muro infranqueable sin el humano
	}

	// 3. Revisión del historial para detectar bucles de falla (Errores en logs)
	errorCount := 0
	for _, msg := range state.History {
		if strings.Contains(strings.ToLower(msg), "error") || strings.Contains(strings.ToLower(msg), "fail") {
			errorCount++
		}
	}
	friction += float64(errorCount) * 0.2

	return friction
}

// Global default evaluator
var DefaultEvaluator Evaluator = &HeuristicEvaluator{}

// AnalyzePotentialNode simula brevemente la viabilidad de un nodo
// En un MCTS real, esto expandiría el árbol. Aquí hace un look-ahead simple.
func AnalyzePotentialNode(state *State, nodeName string) float64 {
	// Clonamos superficialmente para no mutar durante la heurística
	simState := &State{
		ID:      state.ID,
		Goal:    state.Goal,
		Branch:  nodeName,
		Status:  state.Status,
		History: state.History, // Read-only look
		Errors:  state.Errors,
	}

	// Evaluar la fricción inicial
	baseFriction := DefaultEvaluator.EvaluateFriction(simState)
	
	// Podríamos penalizar nodos específicos si supiéramos que fallan constantemente
	// por ahora retornamos la base
	fmt.Printf("[EVALUATOR] Fricción estimada para rama '%s': %.2f\n", nodeName, baseFriction)
	return baseFriction
}
