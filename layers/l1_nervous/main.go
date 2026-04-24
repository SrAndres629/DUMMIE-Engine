package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
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
	nc         *nats.Conn
	clock      *LamportClock
	universeID string
	lastHash   string
}

func NewNervousSystem(universeID string) *NervousSystem {
	return &NervousSystem{
		clock:      &LamportClock{counter: 0},
		universeID: universeID,
		lastHash:   "0000000000000000000000000000000000000000000000000000000000000000", // Genesis Hash
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

func (ns *NervousSystem) computeCausalHash(parentHash string, payloadHash string, ctx *pb.SixDimensionalContext) string {
	// Canonical concatenation per Spec 02
	// SHA-256(parent_hash + payload_hash + 6d_context)
	contextStr := fmt.Sprintf("%s|%s|%s|%d|%d|%d",
		ctx.LocusX, ctx.LocusY, ctx.LocusZ, ctx.LamportT, int32(ctx.AuthorityA), int32(ctx.IntentI))
	
	content := parentHash + payloadHash + contextStr
	hash := sha256.Sum256([]byte(content))
	return hex.EncodeToString(hash[:])
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
			payload := "PULSE_HEARTBEAT"
			payloadHash := hex.EncodeToString(func() []byte {
				h := sha256.Sum256([]byte(payload))
				return h[:]
			}())
			
			// Contexto Determinista (Spec 12)
			contextObj := &pb.SixDimensionalContext{
				LocusX:      LayerName,
				LocusY:      "core.life",
				LocusZ:      "heartbeat",
				LamportT:    tick,
				AuthorityA:  pb.AuthorityLevel_AGENT,
				IntentI:     pb.IntentType_OBSERVATION,
			}

			causalHash := ns.computeCausalHash(ns.lastHash, payloadHash, contextObj)
			
			// Generar MemoryNode4DTES (Spec 02/10)
			node := &pb.MemoryNode4DTES{
				CausalHash: causalHash,
				ParentHash: ns.lastHash,
				Payload:    []byte(payload),
				PayloadHash: payloadHash,
				Context:    contextObj,
			}

			// Telemetría con EventId (Spec 13)
			if ns.nc != nil {
				data, _ := proto.Marshal(node)
				ns.nc.Publish("core.v2.life.heartbeat", data)
				
				// Simulación de Registro Apache Arrow (Zero-Copy) en Unidad D
				log.Printf("[%s] Pulse: CausalHash=%s (parent: %s) | LamportTick=%d", LayerName, causalHash[:8], ns.lastHash[:8], tick)
			}
			
			ns.lastHash = causalHash
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
