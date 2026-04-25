package orchestrator

import (
	"context"
	"fmt"
	"strings"
	"testing"
)

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
