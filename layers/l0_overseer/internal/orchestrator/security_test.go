package orchestrator

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"testing"
	"time"

	"io.dummie.v2/nervous/pkg/proto/skill"
)

func TestInFlightBlocking(t *testing.T) {
	sm := &SkillManager{}
	g := NewStateGraph(sm, nil)
	
	// Nodo que tarda en responder
	g.AddNode("SlowNode", func(ctx context.Context, s *State) (*State, error) {
		time.Sleep(100 * time.Millisecond)
		return s, nil
	})

	daemon := NewDaemon(g, nil)
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go daemon.schedulerLoop(ctx)

	state := &State{ID: "TASK-123", Goal: "In-Flight Test", Branch: "SlowNode"}

	// 1. Enviar tarea
	daemon.Tasks <- state
	time.Sleep(20 * time.Millisecond) // Dejar que empiece

	daemon.InFlightMu.Lock()
	if !daemon.InFlight["TASK-123"] {
		daemon.InFlightMu.Unlock()
		t.Fatal("La tarea debería estar In-Flight")
	}
	daemon.InFlightMu.Unlock()

	// 2. Enviar duplicado
	daemon.Tasks <- state
	time.Sleep(50 * time.Millisecond)

	// El duplicado no debería haber lanzado otra goroutine que resetee el tiempo o algo similar
	// Pero lo más importante es verificar que el mapa sigue teniendo solo uno (que es el original)
	
	time.Sleep(150 * time.Millisecond) // Esperar a que termine la original

	daemon.InFlightMu.Lock()
	if daemon.InFlight["TASK-123"] {
		daemon.InFlightMu.Unlock()
		t.Fatal("La tarea debería haber salido de In-Flight")
	}
	daemon.InFlightMu.Unlock()
	
	fmt.Println("[✓] In-Flight Blocking Test Passed.")
}

func TestStatePersistenceExtended(t *testing.T) {
	dbPath := filepath.Join(t.TempDir(), "test_security.db")
	store, err := NewStateStore(dbPath)
	if err != nil {
		t.Fatalf("Error creando store: %v", err)
	}
	defer store.Close()

	testSkill := &skill.Skill{Id: "test-skill", TechnicalName: "Test"}
	testErr := fmt.Errorf("sample error")

	state := &State{
		ID:     "SecurityAgent",
		Goal:   "Test Extended Persistence",
		Skills: []*skill.Skill{testSkill},
		Errors: []error{testErr},
	}

	err = store.SaveState(state)
	if err != nil {
		t.Fatalf("Error guardando estado: %v", err)
	}

	all, err := store.LoadAll()
	if err != nil {
		t.Fatalf("Error cargando estados: %v", err)
	}

	if len(all) == 0 {
		t.Fatal("No se recuperó el estado")
	}

	recovered := all[0]
	if len(recovered.Skills) == 0 || recovered.Skills[0].Id != "test-skill" {
		t.Errorf("Skills no persistidas correctamente: %v", recovered.Skills)
	}

	if len(recovered.Errors) == 0 || recovered.Errors[0].Error() != "sample error" {
		t.Errorf("Errors no persistidos correctamente: %v", recovered.Errors)
	}

	fmt.Println("[✓] Extended Persistence Test Passed (Skills & Errors recovered).")
}

func TestSocketCleanup(t *testing.T) {
	tempDir := t.TempDir()
	socketPath := filepath.Join(tempDir, "test.sock")
	
	daemon := &Daemon{socketPath: socketPath}
	
	// Crear un archivo falso para simular el socket
	err := os.WriteFile(socketPath, []byte("test"), 0644)
	if err != nil {
		t.Fatalf("Error creando socket fake: %v", err)
	}

	if _, err := os.Stat(socketPath); os.IsNotExist(err) {
		t.Fatal("El socket fake debería existir")
	}

	daemon.Cleanup()

	if _, err := os.Stat(socketPath); !os.IsNotExist(err) {
		t.Error("El socket fake debería haber sido eliminado")
	}

	fmt.Println("[✓] Socket Cleanup Test Passed.")
}
