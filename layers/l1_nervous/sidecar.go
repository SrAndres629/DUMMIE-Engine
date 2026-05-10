package main

import (
	"context"
	"log"

	"github.com/nats-io/nats.go"
)

// IOSidecar (L1) - Bridge para Model Context Protocol (MCP)
// Este sidecar permite a las capas superiores (Brain/L2) inyectar herramientas
// y contexto a través del bus de NATS.
type IOSidecar struct {
	nc *nats.Conn
}

func NewIOSidecar(nc *nats.Conn) *IOSidecar {
	return &IOSidecar{nc: nc}
}

func (s *IOSidecar) Start(ctx context.Context) {
	// Suscribirse a solicitudes de MCP (Spec 15)
	sub, err := s.nc.Subscribe("core.v2.mcp.request", func(m *nats.Msg) {
		log.Printf("[L1-Sidecar] MCP Request recibida: %s", string(m.Data))
		// Lógica de ruteo hacia L2 o ejecución directa si es atómica
		s.nc.Publish(m.Reply, []byte("ACK_MCP_V2_L1"))
	})

	if err != nil {
		log.Fatalf("[!] Error al iniciar Sidecar MCP: %v", err)
	}

	log.Println("[+] Sidecar de I/O (MCP) activo en core.v2.mcp.request")

	<-ctx.Done()
	sub.Unsubscribe()
}
