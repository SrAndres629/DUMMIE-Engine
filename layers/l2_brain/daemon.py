import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

# Importaciones Isomórficas (Flat Structure)
from gateway_contract import GatewayRequest, SagaTransaction, SagaStep
from auditor_port import BaseAuditor, BaseExecutor

# Importaciones de Adaptadores (Cruce de Capas vía PYTHONPATH)
try:
    from topological_auditor import TopologicalAuditor
    from budget_auditor import BudgetAuditor
    from compliance_auditor import ComplianceAuditor
    from mcp_driver import MCPDriver as MuscleDriver
except ImportError as e:
    logging.getLogger("dummie-daemon").error(f"Tabula Rasa Import Error: {e}")
    TopologicalAuditor = None
    BudgetAuditor = None
    ComplianceAuditor = None
    MuscleDriver = None

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
    def __init__(
        self,
        ledger_path: str,
        mcp_gateway: Any,
        event_bus: EventBus,
        skill_binder: Optional[Any] = None,
    ):
        self.ledger_path = ledger_path
        self.mcp_gateway = mcp_gateway
        self.event_bus = event_bus
        self.skill_binder = skill_binder
        self.active_transactions: Dict[str, SagaTransaction] = {}
        self.concurrency_limit = asyncio.Semaphore(5)
        self.last_plan: Dict[str, Any] = {}
        self.last_task_routes: List[Dict[str, str]] = []
        
        # Capas Somáticas (Conexión Directa)
        self.s_shield: BaseAuditor = TopologicalAuditor() if TopologicalAuditor else _AllowAllAuditor()
        self.e_shield: BaseAuditor = BudgetAuditor() if BudgetAuditor else _AllowAllAuditor()
        self.l_shield: BaseAuditor = ComplianceAuditor() if ComplianceAuditor else _AllowAllAuditor()
        self.muscle: BaseExecutor = MuscleDriver(mcp_gateway) if MuscleDriver else _NoopExecutor()

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
        
        # [COGNITIVE LOOP] Haz de Hipótesis y Colapso Entrópico
        try:
            from domain.dtos import HypothesisBundle, Hypothesis
            from domain.hypothesis_service import HypothesisService
        except ImportError:
            from layers.l2_brain.domain.dtos import HypothesisBundle, Hypothesis
            from layers.l2_brain.domain.hypothesis_service import HypothesisService

        bundle = HypothesisBundle(
            bundle_id=transaction_id,
            hypotheses=[
                Hypothesis(hypothesis_id="optimal_path", content="Ejecución óptima directa", weight=0.7),
                Hypothesis(hypothesis_id="fallback_path", content="Reintento o compensación parcial", weight=0.2),
                Hypothesis(hypothesis_id="abort_path", content="Fallo irrecuperable", weight=0.1)
            ]
        )
        entropy = HypothesisService.calculate_entropy(bundle)
        logger.info(f"Cognitive loop HypothesisBundle initial entropy: {entropy}")

        try:
            # Auditoría Jidoka Triple
            for shield, name in [(self.s_shield, "S"), (self.e_shield, "E"), (self.l_shield, "L")]:
                ok, msg = await shield.audit(request.dag_xml, request.goal)
                if not ok:
                    raise RuntimeError(f"VETO [{name}]: {msg}")

            import xml.etree.ElementTree as ET
            root = ET.fromstring(request.dag_xml)
            plan = self._build_hierarchical_plan(request, root)
            self.last_plan = plan
            self.last_task_routes = []

            for idx, task in enumerate(root.findall("task"), start=1):
                route = self._route_task_with_plan(task, plan, idx)
                self.last_task_routes.append(route)
                await self._dispatch_task(task, saga, route)
                
            logger.info(f"Saga Success: {transaction_id}")
            return self._build_outcome("SUCCESS", transaction_id, saga)
        except Exception as e:
            logger.error(f"Saga Failure: {e}")
            await self._compensate(saga)
            return self._build_outcome("FAILED", transaction_id, saga, str(e))

    async def _dispatch_task(self, task_node: Any, saga: SagaTransaction, route: Dict[str, str]):
        task_id = task_node.get("id")
        step = SagaStep(task_id=task_id)
        saga.steps.append(step)

        if not route.get("master_skill") or not route.get("subskill_id"):
            raise RuntimeError(f"Task {task_id} skipped hierarchical planning gate")

        # [COGNITIVE LOOP] Inferencia Contrafactual do(a) Pearl
        try:
            from domain.counterfactual_service import CounterfactualService
        except ImportError:
            from layers.l2_brain.domain.counterfactual_service import CounterfactualService
            
        tool_name = task_node.get("tool")
        utility_score = CounterfactualService.evaluate_intervention(
            action_a=tool_name,
            context_x=saga.transaction_id,
            utility_function=lambda a, x: 1.0 if a else 0.0,
            cost_lambda=0.1,
            cost_function=lambda a: 0.5 if "destructive" in str(a).lower() else 0.1
        )
        logger.info(f"Counterfactual do({tool_name}) evaluation score: {utility_score}")

        response = await self.muscle.execute(
            server_name=task_node.get("server", "filesystem"),
            tool_name=task_node.get("tool"),
            arguments=json.loads(task_node.find("arguments").text or "{}")
        )
        
        if "error" in response:
            step.status = "FAILED"
            raise RuntimeError(f"Physical Error in {task_id}")
        
        step.status = "DONE"

    def _build_hierarchical_plan(self, request: GatewayRequest, dag_root: Any) -> Dict[str, Any]:
        preferred_master = (dag_root.get("master_skill") or "").strip()
        if self.skill_binder:
            plan = self.skill_binder.propose_reflective_plan(request.goal, preferred_master)
        else:
            plan = {
                "goal": request.goal,
                "plan_type": "hierarchical_fallback",
                "master_skill": preferred_master or "sw.master.default",
                "steps": [
                    {"order": 1, "skill_id": "sw.subskill.dispatch", "name": "dispatch"}
                ],
            }

        steps = plan.get("steps", []) if isinstance(plan, dict) else []
        master_skill = plan.get("master_skill", "") if isinstance(plan, dict) else ""
        if not master_skill or not isinstance(steps, list) or not steps:
            raise RuntimeError("Hierarchical planner returned an invalid plan")
        return plan

    def _route_task_with_plan(
        self,
        task_node: Any,
        plan: Dict[str, Any],
        task_index: int,
    ) -> Dict[str, str]:
        steps = plan.get("steps", [])
        selected_skill = str(task_node.get("subskill") or task_node.get("skill_id") or "").strip()

        if not selected_skill:
            tool_name = str(task_node.get("tool") or "").strip().lower()
            for step in steps:
                skill_id = str(step.get("skill_id", "")).strip()
                skill_name = str(step.get("name", "")).strip().lower()
                if tool_name and (tool_name in skill_id.lower() or tool_name == skill_name):
                    selected_skill = skill_id
                    break

        if not selected_skill:
            selected_idx = min(max(task_index - 1, 0), len(steps) - 1)
            selected = steps[selected_idx]
            selected_skill = str(selected.get("skill_id", "")).strip()

        route = {
            "task_id": task_node.get("id", ""),
            "master_skill": str(plan.get("master_skill", "")).strip(),
            "subskill_id": selected_skill,
        }
        if not route["subskill_id"]:
            raise RuntimeError(f"Task {route['task_id']} has no subskill route")
        return route

    async def _compensate(self, saga: SagaTransaction):
        logger.warning(f"Saga Compensation Initiated: {saga.transaction_id}")
        for step in reversed(saga.steps):
            step.status = "COMPENSATED"

    def _build_outcome(
        self,
        status: str,
        transaction_id: str,
        saga: SagaTransaction,
        error: str = "",
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "transaction_id": transaction_id,
            "error": error,
            "steps": [{"task_id": step.task_id, "status": step.status} for step in saga.steps],
        }


class _AllowAllAuditor(BaseAuditor):
    async def audit(self, dag_xml: str, goal: str = ""):
        return True, "BYPASS"


class _NoopExecutor(BaseExecutor):
    async def execute(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": True}
