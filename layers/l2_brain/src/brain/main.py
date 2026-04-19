import asyncio
import os
import signal
import nats
import json
from pydantic_ai import Agent
from pydantic import BaseModel

# === Importar Escudo Nativo (L3-Rust) ===
try:
    import shield # type: ignore
    print("[L2-Brain] Escudo (L3-Rust) cargado exitosamente.")
except ImportError:
    print("[L2-Brain] !!! ADVERTENCIA: Escudo (L3) no encontrado. Operando sin protección !!!")
    shield = None

# === Modelos de Intención (Spec 12/21) ===
class AgentIntent(BaseModel):
    intent_type: str
    target: str
    rationale: str
    risk_score: float = 0.5

class BrainSystem:
    def __init__(self):
        self.nc = None
        self.is_running = True

    async def connect(self):
        nats_url = os.getenv("NATS_URL", "nats://127.0.0.1:4222")
        try:
            self.nc = await nats.connect(nats_url)
            print(f"[L2-Brain] Conectado a NATS en {nats_url}")
        except Exception as e:
            print(f"[L2-Brain] Error al conectar a NATS: {e}")

    async def listen_for_tasks(self):
        if not self.nc:
            return
            
        async def message_handler(msg):
            subject = msg.subject
            data = msg.data.decode()
            print(f"[L2-Brain] Tarea recibida: {data}")
            
            # 1. Simulación de Intención Generada por PydanticAI (Spec 21)
            intent = AgentIntent(
                intent_type="delete_root" if "VETO" in data else "read_file",
                target="/",
                rationale="Mantenimiento sistémico",
                risk_score=0.9 if "VETO" in data else 0.1
            )
            
            # 2. Validación vía Escudo (L3-Rust) - Spec 31
            if shield:
                audit_result_json = shield.audit_intent(intent.model_dump_json())
                audit_result = json.loads(audit_result_json)
                
                if not audit_result.get("authorized"):
                    print(f"[L2-Brain] !!! VETO DEL ESCUDO (L3) !!! Motivo: {audit_result.get('shield_note')}")
                    await msg.respond(b"VETO_L3_SECURITY_VIOLATION")
                    return
                
                print(f"[L2-Brain] Intención autorizada por L3: {audit_result.get('shield_note')}")

            await msg.respond(b"INTENT_QUEUED_L2_VALIDATED")

        await self.nc.subscribe("core.v2.orchestration.tasks", cb=message_handler)
        print("[L2-Brain] Escuchando tareas en core.v2.orchestration.tasks")

    async def run(self):
        await self.connect()
        await self.listen_for_tasks()
        
        while self.is_running:
            await asyncio.sleep(1)

    async def stop(self):
        self.is_running = False
        if self.nc:
            await self.nc.close()

async def main():
    brain = BrainSystem()
    
    # Manejo de Apoptosis (Spec 03)
    loop = asyncio.get_running_loop()
    
    def stop_signal():
        asyncio.create_task(brain.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_signal)

    print("=== L2_BRAIN: Motor Cognitivo (Python/PydanticAI) Iniciado ===")
    try:
        await brain.run()
    except asyncio.CancelledError:
        pass
    print("=== L2_BRAIN: Apoptosis Causal Controlada ===")

if __name__ == "__main__":
    asyncio.run(main())
