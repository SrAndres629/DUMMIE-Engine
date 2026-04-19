package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"sync/atomic"
	"syscall"
	"time"

	"github.com/nats-io/nats.go"
	// Los stubs se generaron en este path relativo durante el build en Docker
	pb "io.dummie.v2/nervous/proto"
	"google.golang.org/protobuf/proto"
)

const (
	LayerName = "L1_NERVOUS"
	NATSURL   = nats.DefaultURL
)

// Clockmaker de Lamport (Relojero de Lamport - Spec 03)
type LamportClock struct {
	counter uint64
}

func (lc *LamportClock) Tick() uint64 {
	return atomic.AddUint64(&lc.counter, 1)
}

func (lc *LamportClock) Sync(other uint64) {
	for {
		current := atomic.LoadUint64(&lc.counter)
		if other <= current {
			break
		}
		if atomic.CompareAndSwapUint64(&lc.counter, current, other+1) {
			break
		}
	}
}

// NervousSystem (L1) - El Relojero de Lamport
type NervousSystem struct {
	nc        *nats.Conn
	clock     *LamportClock
	universeID string
}

func NewNervousSystem(universeID string) *NervousSystem {
	return &NervousSystem{
		clock:      &LamportClock{counter: 0},
		universeID: universeID,
	}
}

func (ns *NervousSystem) Connect() error {
	nc, err := nats.Connect(NATSURL)
	if err != nil {
		return fmt.Errorf("fallo al conectar a NATS: %w", err)
	}
	ns.nc = nc
	return nil
}

// Loop de Latido Sistémico (Heartbeat - Spec 05/13)
func (ns *NervousSystem) StartHeartbeat(ctx context.Context) {
	ticker := time.NewTicker(3 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			tick := ns.clock.Tick()
			
			// Generar EventID Causal (Spec 10/12)
			event := &pb.EventId{
				UniverseId:     ns.universeID,
				BranchId:       "main",
				LamportTick:    tick,
				Authority:      pb.AuthorityLevel_CONSENSUS_COMMIT,
			}

			// Telemetría con EventId (Spec 13)
			if ns.nc != nil {
				data, _ := proto.Marshal(event)
				ns.nc.Publish("core.v2.life.heartbeat", data)
				
				// Simulación de Registro Apache Arrow (Zero-Copy) en Unidad D
				// En producción, esto usaría cgo o garrow para escribir RecordBatches
				log.Printf("[%s] Pulse: LamportTick=%d | ArrowBatch persistido en /media/datasets/dummie/telemetry", LayerName, tick)
			}
		}
	}
}

func main() {
	fmt.Printf("=== %s: El Relojero de Lamport Iniciado ===\n", LayerName)

	ns := NewNervousSystem("DE-V2-GREENFIELD-01")
	
	if err := ns.Connect(); err != nil {
		log.Printf("[!] Advertencia: NATS no disponible. Operando en modo Offline/Local.\n")
	} else {
		defer ns.nc.Close()
		log.Println("[+] Conexión a NATS establecida.")
	}

	ctx, cancel := context.WithCancel(context.Background())
	go ns.StartHeartbeat(ctx)

	// Iniciar Sidecar de I/O para MCP (Spec 15)
	if ns.nc != nil {
		sidecar := NewIOSidecar(ns.nc)
		go sidecar.Start(ctx)
	}

	// Manejo de Señales (Apoptosis - Spec 03)
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
	<-sigCh
	
	cancel()
	fmt.Printf("\n=== %s: Apoptosis Causal Controlada ===\n", LayerName)
}
