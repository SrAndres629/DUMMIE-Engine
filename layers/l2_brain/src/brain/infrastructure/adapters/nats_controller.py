import os
import nats
import json
from datetime import datetime
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError
from brain.application.interfaces import IBrainOrchestrator

# Protobuf imports for L1/L2 Causal Sync (Spec 03)
# Note: Ensure the proto path is in PYTHONPATH
try:
    from proto.dummie.v2.memory_pb2 import MemoryNode4DTES
except ImportError:
    # Fallback if proto generation is not in standard path
    MemoryNode4DTES = None

class NatsController:
    def __init__(self, input_port: IBrainOrchestrator):
        self.input_port = input_port
        self.nc = None
        self.is_running = True

    async def connect(self):
        nats_url = os.getenv("NATS_URL", "nats://127.0.0.1:4222")
        try:
            self.nc = await nats.connect(nats_url)
            print(f"[NatsController] Conectado a NATS en {nats_url}")
        except Exception as e:
            print(f"[NatsController] Error al conectar a NATS: {e}")

    async def publish_event(self, subject: str, payload: bytes):
        """Publica un evento en NATS."""
        if self.nc and self.nc.is_connected:
            await self.nc.publish(subject, payload)
        else:
            print(f"[NATSController] Error: No conectado. Omitiendo {subject}")

    async def emit_heartbeat(self, agent_id: str, expertise: list):
        """Emite latidos de presencia (Spec 37)."""
        subject = "ao.v2.l2.brain.presence"
        heartbeat = {
            "agent_id": agent_id,
            "expertise_tags": expertise,
            "current_load": 0.1, # Mock
            "authority_level": "AGENT",
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.publish_event(subject, json.dumps(heartbeat).encode())
        print(f"[NATSController] Heartbeat emitido: {subject}")

    async def listen_for_tasks(self):
        if not self.nc:
            return

        # 1. Escuchar el Pulso de Vida (L1 Heartbeats) para sincronía causal (Spec 03)
        async def heartbeat_handler(msg):
            if MemoryNode4DTES is None:
                return
            try:
                node = MemoryNode4DTES()
                node.ParseFromString(msg.data)
                # Sincronizar Reloj de Lamport con L1
                self.input_port.sync_clock(node.context.lamport_t)
            except Exception as e:
                # Silencioso para no inundar el log en heartbeats de alta frecuencia
                pass

        await self.nc.subscribe("core.v2.life.heartbeat.full", cb=heartbeat_handler)
        print("[NatsController] Escuchando Pulso Causal (core.v2.life.heartbeat.full)")

        # 2. Escuchar tareas de orquestación
        async def message_handler(msg):
            data = msg.data.decode()
            response = await self.input_port.handle_task(data)
            await msg.respond(response.encode())

        await self.nc.subscribe("core.v2.orchestration.tasks", cb=message_handler)
        print("[NatsController] Escuchando tareas en core.v2.orchestration.tasks")

    async def stop(self):
        self.is_running = False
        if self.nc:
            await self.nc.close()
