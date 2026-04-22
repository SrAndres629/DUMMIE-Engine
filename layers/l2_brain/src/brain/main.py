import asyncio
import signal
from brain.infrastructure.adapters.shield_adapter import NativeShieldAdapter
from brain.application.use_cases.orchestrator import CognitiveOrchestrator
from brain.infrastructure.adapters.nats_controller import NatsController

async def main():
    print("=== L2_BRAIN: Motor Cognitivo (Arquitectura Hexagonal) Iniciado ===")
    
    # 1. Instanciar Adaptadores de Salida (Infrastructure)
    shield_adapter = NativeShieldAdapter()
    from brain.infrastructure.adapters.kuzu_repository import KuzuRepository, KuzuSkillRepository
    from brain.infrastructure.adapters.ledger_adapter import DecisionLedgerAdapter
    
    kuzu_repo = KuzuRepository()
    skill_repo = KuzuSkillRepository(kuzu_repo)
    ledger_adapter = DecisionLedgerAdapter()
    
    # 2. Instanciar Casos de Uso (Application)
    # Nota: El orquestador ahora inyecta el caso de uso de cristalización internamente
    orchestrator = CognitiveOrchestrator(
        shield_port=shield_adapter,
        event_store=kuzu_repo,
        ledger_audit=ledger_adapter,
        skill_repo=skill_repo
    )
    
    # 3. Instanciar Controladores de Entrada (Infrastructure)
    nats_controller = NatsController(input_port=orchestrator)
    
    # Conectar y Escuchar
    await nats_controller.connect()
    await nats_controller.listen_for_tasks()

    # Manejo de Apoptosis (Spec 03)
    loop = asyncio.get_running_loop()
    
    def stop_signal():
        asyncio.create_task(nats_controller.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_signal)

    try:
        while nats_controller.is_running:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
        
    print("=== L2_BRAIN: Apoptosis Causal Controlada ===")

if __name__ == "__main__":
    asyncio.run(main())
