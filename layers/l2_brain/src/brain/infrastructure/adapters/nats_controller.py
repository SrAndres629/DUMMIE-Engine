import os
import nats
from brain.application.interfaces import IBrainOrchestrator

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

    async def listen_for_tasks(self):
        if not self.nc:
            return
            
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
