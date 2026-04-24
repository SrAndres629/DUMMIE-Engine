import asyncio
import json
import logging
import fcntl
from typing import Dict, Any, List
from datetime import datetime
from abc import ABC, abstractmethod

# Importaciones Isomórficas (Flat Structure)
from gateway_contract import GatewayRequest, SagaTransaction, SagaStep, CompensatoryAction
from auditor_port import BaseAuditor, BaseExecutor

# Importaciones de Adaptadores (Cruce de Capas vía PYTHONPATH)
try:
    from topological_auditor import TopologicalAuditor
    from budget_auditor import BudgetAuditor
    from compliance_auditor import ComplianceAuditor
    from mcp_driver import MCPDriver as MuscleDriver
except ImportError as e:
    logging.getLogger("dummie-daemon").error(f"Tabula Rasa Import Error: {e}")

logger = logging.getLogger("dummie-daemon")

class EventBus(ABC):
    @abstractmethod
    async def wait_for_request(self) -> GatewayRequest:
        pass

class DummieDaemon:
    """
    [L2_BRAIN] Orquestador Supremo Antigravity.
    Estructura Tabula Rasa: Flat, Determinista e Industrial.
    """
    def __init__(self, ledger_path: str, mcp_gateway: Any, event_bus: EventBus):
        self.ledger_path = ledger_path
        self.mcp_gateway = mcp_gateway
        self.event_bus = event_bus
        self.active_transactions: Dict[str, SagaTransaction] = {}
        self.concurrency_limit = asyncio.Semaphore(5)
        
        # Capas Somáticas (Conexión Directa)
        self.s_shield: BaseAuditor = TopologicalAuditor()
        self.e_shield: BaseAuditor = BudgetAuditor()
        self.l_shield: BaseAuditor = ComplianceAuditor()
        self.muscle: BaseExecutor = MuscleDriver(mcp_gateway)

    async def run_forever(self):
        logger.info("Antigravity Daemon: ONLINE (TABULA RASA MODE)")
        while True:
            try:
                request = await self.event_bus.wait_for_request()
                if request:
                    asyncio.create_task(self._process_request_safe(request))
            except Exception as e:
                logger.error(f"Cycle Failure: {e}")
                await asyncio.sleep(5)

    async def _process_request_safe(self, request: GatewayRequest):
        async with self.concurrency_limit:
            await self.process_request(request)

    async def process_request(self, request: GatewayRequest):
        transaction_id = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        context_token = f"TOKEN-{hash(transaction_id)}"
        saga = SagaTransaction(transaction_id=transaction_id, context_token=context_token)
        self.active_transactions[transaction_id] = saga

        logger.info(f"Saga Start: {transaction_id} | Goal: {request.goal}")
        
        try:
            # Auditoría Jidoka Triple
            for shield, name in [(self.s_shield, "S"), (self.e_shield, "E"), (self.l_shield, "L")]:
                ok, msg = await shield.audit(request.dag_xml, request.goal)
                if not ok:
                    raise RuntimeError(f"VETO [{name}]: {msg}")

            import xml.etree.ElementTree as ET
            root = ET.fromstring(request.dag_xml)
            for task in root.findall("task"):
                await self._dispatch_task(task, saga)
                
            logger.info(f"Saga Success: {transaction_id}")
        except Exception as e:
            logger.error(f"Saga Failure: {e}")
            await self._compensate(saga)

    async def _dispatch_task(self, task_node: Any, saga: SagaTransaction):
        task_id = task_node.get("id")
        step = SagaStep(task_id=task_id)
        saga.steps.append(step)

        response = await self.muscle.execute(
            server_name=task_node.get("server", "filesystem"),
            tool_name=task_node.get("tool"),
            arguments=json.loads(task_node.find("arguments").text or "{}")
        )
        
        if "error" in response:
            step.status = "FAILED"
            raise RuntimeError(f"Physical Error in {task_id}")
        
        step.status = "DONE"

    async def _compensate(self, saga: SagaTransaction):
        logger.warning(f"Saga Compensation Initiated: {saga.transaction_id}")
        for step in reversed(saga.steps):
            step.status = "COMPENSATED"
