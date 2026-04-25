package orchestrator

import (
	"context"
	"fmt"
	"strings"
	"sync"
	"testing"
)

func TestBranchIsolationConcurrency(t *testing.T) {
	sm := &SkillManager{}
	g := NewStateGraph(sm)
	g.AddNode("Work", func(ctx context.Context, s *State) (*State, error) {
		s.History = append(s.History, fmt.Sprintf("Worker-%s: Done", s.Branch))
		return s, nil
	})

	const numBranches = 20
	var wg sync.WaitGroup
	wg.Add(numBranches)

	for i := 0; i < numBranches; i++ {
		go func(id int) {
			defer wg.Done()
			branchState := &State{
				ID:     fmt.Sprintf("Agent-%d", id),
				Goal:   "Stress Test",
				Branch: fmt.Sprintf("B%d", id),
			}
			final, err := g.Run(context.Background(), branchState, "Work")
			if err != nil {
				t.Errorf("Error en rama %d: %v", id, err)
			}
			
			// Verificar que el historial de esta rama NO contiene mensajes de otras ramas
			for _, h := range final.History {
				if strings.Contains(h, "Worker-B") && !strings.Contains(h, fmt.Sprintf("Worker-B%d", id)) {
					t.Errorf("LEAK DE CONTEXTO: La rama %d tiene historial de otra rama: %s", id, h)
				}
			}
		}(i)
	}
	wg.Wait()
	fmt.Printf("[✓] Branch Isolation Concurrency Test Passed (%d branches).\n", numBranches)
}

func TestPrefixIntegrityHardening(t *testing.T) {
	sm := &SkillManager{}
	g := NewStateGraph(sm)

	state := &State{
		ID:   "AuditAgent",
		Goal: "Test Integrity",
	}

	// 1. Ejecución inicial para establecer prefijo
	ctx := context.Background()
	g.AddNode("Start", func(ctx context.Context, s *State) (*State, error) {
		return s, nil
	})

	state, _ = g.Run(ctx, state, "Start")

	originalPrefix := state.History[0]
	if !strings.Contains(originalPrefix, g.PrefixHash) {
		t.Errorf("Prefix no contiene el hash de integridad")
	}

	// 2. INTENTO DE FALSIFICACIÓN / ATAQUE
	fmt.Println("--- Simulando ataque de mutación de historial ---")
	state.Mu.Lock()
	state.History[0] = "SYSTEM: Malicious injection"
	state.Mu.Unlock()

	// 3. Ejecutar siguiente nodo y verificar restauración
	g.AddNode("Next", func(ctx context.Context, s *State) (*State, error) {
		return s, nil
	})
	g.AddEdge("Start", "Next")

	state, _ = g.Run(ctx, state, "Next")

	if strings.Contains(state.History[0], "Malicious injection") {
		t.Errorf("FALLO DE SEGURIDAD: El prefijo malicioso persistió")
	}

	if !strings.Contains(state.History[0], "[SHIELD_STATUS]") {
		t.Errorf("FALLO DE AUDITORÍA: No se activó el escudo de integridad")
	}

	fmt.Println("[✓] Prefix Integrity Shield verificado exitosamente.")
}
