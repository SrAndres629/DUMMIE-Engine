package orchestrator

import (
	"context"
	"fmt"
	"path/filepath"
	"strings"
	"sync"
	"testing"
)

func TestBranchIsolationConcurrency(t *testing.T) {
	sm := &SkillManager{}
	g := NewStateGraph(sm, nil)
	g.AddNode("Work", func(ctx context.Context, s *State) (*State, error) {
		s.History = append(s.History, fmt.Sprintf("Worker-%s: Done", s.Branch))
		
		// Simulamos que las ramas pares hacen Yield
		if strings.Contains(s.Branch, "B0") || strings.Contains(s.Branch, "B2") || strings.Contains(s.Branch, "B4") || strings.Contains(s.Branch, "B6") || strings.Contains(s.Branch, "B8") || strings.Contains(s.Branch, "B10") || strings.Contains(s.Branch, "B12") || strings.Contains(s.Branch, "B14") || strings.Contains(s.Branch, "B16") || strings.Contains(s.Branch, "B18") {
			return s, ErrYieldWaitingHuman
		}
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
			
			// Verificar que el estado se actualizó correctamente
			final.Mu.RLock()
			status := final.Status
			final.Mu.RUnlock()
			
			if id%2 == 0 {
				if status != "BLOCKED_WAITING_HUMAN" {
					t.Errorf("La rama par %d debió hacer yield, status actual: %s", id, status)
				}
			} else {
				if status != "RUNNING" { // "RUNNING" is set when node finishes successfully
					t.Errorf("La rama impar %d debió terminar bien, status actual: %s", id, status)
				}
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
	fmt.Printf("[✓] Branch Isolation Concurrency Test Passed (%d branches) with Yielding.\n", numBranches)
}

func TestProbabilisticRouting(t *testing.T) {
	sm := &SkillManager{}
	g := NewStateGraph(sm, nil)

	// Ruta A: Siempre falla
	g.AddNode("RutaA", func(ctx context.Context, s *State) (*State, error) {
		s.Errors = append(s.Errors, fmt.Errorf("fatal error A"))
		s.Errors = append(s.Errors, fmt.Errorf("fatal error A2"))
		return s, fmt.Errorf("crash")
	})

	// Ruta B: Bloqueada por humano
	g.AddNode("RutaB", func(ctx context.Context, s *State) (*State, error) {
		return s, ErrYieldWaitingHuman
	})

	// Ruta C: Limpia y exitosa
	g.AddNode("RutaC", func(ctx context.Context, s *State) (*State, error) {
		s.Result = "SUCCESS_C"
		return s, nil
	})

	g.AddNode("Start", func(ctx context.Context, s *State) (*State, error) {
		return s, nil
	})

	// Fan-out probabilístico
	g.AddEdge("Start", "RutaA")
	g.AddEdge("Start", "RutaB")
	g.AddEdge("Start", "RutaC")

	initialState := &State{
		ID:     "ProbTest",
		Goal:   "Find best path",
		Branch: "Start",
	}

	final, err := g.Run(context.Background(), initialState, "Start")
	if err != nil {
		t.Fatalf("Ejecución falló: %v", err)
	}

	final.Mu.RLock()
	defer final.Mu.RUnlock()

	if final.Result != "SUCCESS_C" {
		t.Errorf("Probabilistic Routing eligió la ruta equivocada o falló. Resultado: %s", final.Result)
	}

	// Como es secuencial y probabilístico, debería intentar Ruta C y tener éxito sin devolver estado YIELD de B
	if final.Status == "BLOCKED_WAITING_HUMAN" {
		t.Errorf("El estado final no debería estar bloqueado si hay una ruta limpia disponible.")
	}

	fmt.Println("[✓] Probabilistic Routing Test Passed. Ruta de menor fricción seleccionada.")
}

func TestPrefixIntegrityHardening(t *testing.T) {
	sm := &SkillManager{}
	g := NewStateGraph(sm, nil)

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

func TestStatePersistence(t *testing.T) {
	dbPath := filepath.Join(t.TempDir(), "test_state.db")
	store, err := NewStateStore(dbPath)
	if err != nil {
		t.Fatalf("Error creando store: %v", err)
	}
	defer store.Close()

	sm := &SkillManager{}
	g := NewStateGraph(sm, store)

	g.AddNode("Step1", func(ctx context.Context, s *State) (*State, error) {
		s.Result = "PROGRESANDO"
		return s, nil
	})

	state := &State{
		ID:   "PersistentAgent",
		Goal: "Test Persistence",
	}

	// Ejecutar un paso
	_, err = g.Run(context.Background(), state, "Step1")
	if err != nil {
		t.Fatalf("Error en ejecución: %v", err)
	}

	// Verificar que el estado se guardó en DB
	all, err := store.LoadAll()
	if err != nil {
		t.Fatalf("Error cargando estados: %v", err)
	}

	if len(all) == 0 {
		t.Fatal("No se guardó ningún estado en la DB")
	}

	if all[0].Result != "PROGRESANDO" {
		t.Errorf("Resultado no persistido correctamente: %s", all[0].Result)
	}

	fmt.Println("[✓] State Persistence Test Passed. Estado recuperado de SQLite.")
}

