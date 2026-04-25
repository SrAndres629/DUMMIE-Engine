package main

import (
	"context"
	"fmt"
	"io.dummie.v2/overseer/internal/orchestrator"
	"time"
)

func main() {
	sm := &orchestrator.SkillManager{}
	graph := orchestrator.NewStateGraph(sm, nil)

	// 1. Planner Node
	graph.AddNode("Planner", func(ctx context.Context, state *orchestrator.State) (*orchestrator.State, error) {
		fmt.Printf("[PLANNER] Planificando: %s\n", state.Goal)
		state.History = append(state.History, "Planner: Creado plan de ataque.")
		return state, nil
	})

	// 2. Worker Aggressive
	graph.AddNode("AggressiveCoder", func(ctx context.Context, state *orchestrator.State) (*orchestrator.State, error) {
		fmt.Println("[CODER] 🏎️ Ejecución agresiva (Rápida)...")
		time.Sleep(50 * time.Millisecond) // Más rápido
		state.Result = "Resultado Agresivo (Optimizado para velocidad)"
		state.History = append(state.History, "AggressiveCoder: Código generado rápidamente.")
		return state, nil
	})

	// 3. Worker Conservative
	graph.AddNode("ConservativeCoder", func(ctx context.Context, state *orchestrator.State) (*orchestrator.State, error) {
		fmt.Println("[CODER] 🛡️ Ejecución conservadora (Segura)...")
		time.Sleep(200 * time.Millisecond) // Más lento pero seguro
		state.Result = "Resultado Conservador (Optimizado para seguridad)"
		state.History = append(state.History, "ConservativeCoder: Código generado con validaciones extra.")
		return state, nil
	})

	// 4. Merge Node
	graph.AddNode("Reviewer", func(ctx context.Context, state *orchestrator.State) (*orchestrator.State, error) {
		fmt.Printf("[REVIEWER] Evaluando resultado: %s\n", state.Result)
		state.History = append(state.History, "Reviewer: Resultado validado.")
		return state, nil
	})

	// Definir Edges
	graph.AddEdge("Planner", "AggressiveCoder")
	graph.AddEdge("Planner", "ConservativeCoder")
	graph.AddEdge("AggressiveCoder", "Reviewer")
	graph.AddEdge("ConservativeCoder", "Reviewer")

	// Estado Inicial
	state := &orchestrator.State{
		ID:   "Task-001",
		Goal: "Implementar Skill Ingestion Engine V3",
	}

	finalState, err := graph.Run(context.Background(), state, "Planner")
	if err != nil {
		fmt.Printf("Error ejecutando el enjambre: %v\n", err)
		return
	}

	fmt.Printf("\n--- REPORTE FINAL DEL ENJAMBRE ---\n")
	fmt.Printf("Goal: %s\n", finalState.Goal)
	fmt.Printf("Result: %s\n", finalState.Result)
	fmt.Printf("History:\n")
	for _, h := range finalState.History {
		fmt.Printf(" - %s\n", h)
	}
}
