package main

import (
	"context"
	"fmt"
	"log"

	"io.dummie.v2/overseer/internal/orchestrator"
)

func main() {
	fmt.Println("--- DUMMIE ENGINE OVERSEER (L0) STARTING ---")

	// 1. Cargar Skills
	sm, err := orchestrator.NewSkillManager("/home/jorand/Escritorio/DUMMIE Engine/.aiwg/memory/skills_ingested.json")
	if err != nil {
		log.Fatalf("Fallo al cargar skills: %v", err)
	}
	fmt.Printf("[L0] %d habilidades cargadas en el SkillManager.\n", len(sm.Registry.Skills))

	// 2. Inicializar Grafo
	graph := orchestrator.NewStateGraph(sm, nil)

	// 3. Definir Nodo: Planner (Filtrado de Skills)
	graph.AddNode("Planner", func(ctx context.Context, state *orchestrator.State) (*orchestrator.State, error) {
		fmt.Printf("[PLANNER] Analizando objetivo: %s\n", state.Goal)
		
		// Filtrado semántico de habilidades relevantes
		relevantSkills := graph.SkillMgr.FilterSkills("git") // Buscamos cosas de git para el ejemplo
		state.Skills = relevantSkills
		
		state.History = append(state.History, "Planner: Identificadas "+fmt.Sprint(len(relevantSkills))+" habilidades de Git.")
		return state, nil
	})

	// 4. Definir Nodo: Executor (Simulado)
	graph.AddNode("Executor", func(ctx context.Context, state *orchestrator.State) (*orchestrator.State, error) {
		if len(state.Skills) > 0 {
			fmt.Printf("[EXECUTOR] Listo para usar skill: %s\n", state.Skills[0].Id)
			state.Result = "Operación simulada exitosa usando " + state.Skills[0].Id
		} else {
			state.Result = "No se encontraron skills relevantes."
		}
		return state, nil
	})

	// 5. Configurar Flujo
	graph.AddEdge("Planner", "Executor")

	// 6. Ejecución
	initialState := &orchestrator.State{
		ID:   "TASK-001",
		Goal: "Hacer un commit de los cambios actuales",
	}

	finalState, err := graph.Run(context.Background(), initialState, "Planner")
	if err != nil {
		log.Fatalf("Error en la ejecución del grafo: %v", err)
	}

	fmt.Printf("\n--- RESULTADO FINAL ---\nID: %s\nResultado: %s\nHistorial: %v\n", 
		finalState.ID, finalState.Result, finalState.History)
}
