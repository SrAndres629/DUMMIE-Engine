package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/nats-io/nats.go"
)

type InfraError struct {
	Code      string `json:"code"`
	Message   string `json:"message"`
	Layer     string `json:"layer"`
	Component string `json:"component"`
}

func main() {
	natsURL := os.Getenv("NATS_URL")
	if natsURL == "" {
		natsURL = nats.DefaultURL
	}

	nc, err := nats.Connect(natsURL)
	if err != nil {
		log.Fatalf("[L0-OVERSEER] Failed to connect to NATS: %v", err)
	}
	defer nc.Close()

	log.Printf("[L0-OVERSEER] Control Plane iniciado. Monitoreando L1...")

	// Suscribirse a errores de infraestructura de L1
	nc.Subscribe("core.v2.nervous.infra.error", func(m *nats.Msg) {
		var errObj InfraError
		if err := json.Unmarshal(m.Data, &errObj); err != nil {
			log.Printf("[L0-OVERSEER] Error malformado recibido: %s", string(m.Data))
			return
		}
		
		log.Printf("[L0-ALERT] CRITICAL FAILURE IN %s (%s): %s [%s]", 
			errObj.Layer, errObj.Component, errObj.Message, errObj.Code)
		
		// Aquí se podría implementar lógica de auto-reinicio o esgrima (fencing)
	})

	// Suscribirse a latidos de L1 (Relojero de Lamport)
	nc.Subscribe("core.v2.life.heartbeat", func(m *nats.Msg) {
		// Monitoreo de actividad vital
	})

	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
	<-sigCh
	fmt.Println("\n[L0-OVERSEER] Apoptosis controlada.")
}
