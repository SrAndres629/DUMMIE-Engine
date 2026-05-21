import asyncio
import signal

async def main():
    pass # print("=== L2_BRAIN: Motor Cognitivo (Arquitectura Hexagonal) Iniciado ===")
    
    # 1. Instanciar Adaptadores de Salida (Infrastructure) - Lazy Loading
    from brain.infrastructure.adapters.shield_adapter import NativeShieldAdapter
    shield_adapter = NativeShieldAdapter()
    
    # Importaciones pesadas diferidas al interior de main
    from brain.infrastructure.adapters.kuzu_repository import KuzuRepository, KuzuSkillRepository
    from brain.infrastructure.adapters.ledger_adapter import DecisionLedgerAdapter
    from brain.infrastructure.adapters.session_ledger_adapter import SessionLedgerAdapter
    
    kuzu_repo = KuzuRepository()
    skill_repo = KuzuSkillRepository(db=kuzu_repo.db)
    ledger_adapter = DecisionLedgerAdapter()
    session_ledger = SessionLedgerAdapter()
    
    # 2. Instanciar Casos de Uso (Application)
    from brain.application.use_cases.orchestrator import CognitiveOrchestrator
    orchestrator = CognitiveOrchestrator(
        shield_port=shield_adapter,
        event_store=kuzu_repo,
        ledger_audit=ledger_adapter,
        session_ledger=session_ledger,
        skill_repo=skill_repo
    )
    
    # 3. Instanciar Controladores de Entrada (Infrastructure)
    from brain.infrastructure.adapters.nats_controller import NatsController
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
        
    pass # print("=== L2_BRAIN: Apoptosis Causal Controlada ===")

if __name__ == "__main__":
    asyncio.run(main())
