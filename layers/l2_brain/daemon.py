import asyncio
import json
import logging
import os
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
    try:
        from layers.l3_shield.topological_auditor import TopologicalAuditor
        from layers.l3_shield.budget_auditor import BudgetAuditor
        from layers.l3_shield.compliance_auditor import ComplianceAuditor
        from layers.l5_muscle.mcp_driver import MCPDriver as MuscleDriver
    except ImportError as nested_error:
        logging.getLogger("dummie-daemon").error(f"Tabula Rasa Import Error: {e}; fallback import error: {nested_error}")
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
        self.last_gate_status: str = "ALLOW"
        self.last_gate_reasons: List[str] = ["all_guards_passed"]
        self.last_hypothesis_entropy: float = 0.0
        self.last_hypothesis_decision: str = "collapsed"
        self.last_counterfactual_scores: List[float] = []
        self._current_counterfactual_threshold: float = 0.0
        self.last_cognitive_preflight: Dict[str, Any] = {"status": "SKIPPED"}
        
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
        self.last_gate_status = "ALLOW"
        self.last_gate_reasons = ["all_guards_passed"]
        self.last_counterfactual_scores = []
        self._current_counterfactual_threshold = 0.0
        self.last_cognitive_preflight = {"status": "SKIPPED"}

        logger.info(f"Saga Start: {transaction_id} | Goal: {request.goal}")
        
        # [COGNITIVE LOOP] Haz de Hipótesis y Colapso Entrópico
        try:
            from domain.dtos import HypothesisBundle, Hypothesis
            from domain.hypothesis_service import HypothesisService
        except ImportError:
            from layers.l2_brain.domain.dtos import HypothesisBundle, Hypothesis
            from layers.l2_brain.domain.hypothesis_service import HypothesisService

        try:
            # Auditoría Jidoka Triple
            for shield, name in [(self.s_shield, "S"), (self.e_shield, "E"), (self.l_shield, "L")]:
                ok, msg = await shield.audit(request.dag_xml, request.goal)
                if not ok:
                    raise RuntimeError(f"VETO [{name}]: {msg}")

            import xml.etree.ElementTree as ET
            root = ET.fromstring(request.dag_xml)
            self._current_counterfactual_threshold = self._parse_float(root.get("min_counterfactual_score"), 0.0)

            guard_decision = self._evaluate_runtime_guards(root)
            self.last_gate_status = guard_decision.status
            self.last_gate_reasons = list(guard_decision.reasons)
            if guard_decision.status != "ALLOW":
                raise GovernanceGateError("runtime_guard_blocked", guard_decision.status, guard_decision.reasons)

            bundle, entropy_threshold = self._build_hypothesis_bundle(root, transaction_id, HypothesisBundle, Hypothesis)
            entropy = HypothesisService.calculate_entropy(bundle)
            self.last_hypothesis_entropy = entropy
            logger.info(f"Cognitive loop HypothesisBundle initial entropy: {entropy}")
            if not HypothesisService.should_collapse(bundle, entropy_threshold):
                self.last_hypothesis_decision = "review_required"
                raise GovernanceGateError(
                    "high_entropy_requires_review",
                    "REVIEW",
                    ["high_entropy_requires_review"],
                )
            dominant = HypothesisService.collapse_to_dominant(bundle)
            self.last_hypothesis_decision = dominant.hypothesis_id if dominant else "collapsed"

            if self._cognitive_preflight_enabled(root):
                self.last_cognitive_preflight = await self._run_cognitive_preflight(request)

            plan = self._build_hierarchical_plan(request, root)
            self.last_plan = plan
            self.last_task_routes = []

            for idx, task in enumerate(root.findall("task"), start=1):
                route = self._route_task_with_plan(task, plan, idx)
                self.last_task_routes.append(route)
                await self._dispatch_task(task, saga, route)
                
            logger.info(f"Saga Success: {transaction_id}")
            return self._build_outcome("SUCCESS", transaction_id, saga)
        except GovernanceGateError as e:
            logger.warning(f"Saga Gate Halt: {e}")
            self.last_gate_status = e.gate_status
            self.last_gate_reasons = list(e.reasons)
            return self._build_outcome(
                "FAILED",
                transaction_id,
                saga,
                str(e),
                gate_status=e.gate_status,
                gate_reasons=e.reasons,
            )
        except Exception as e:
            logger.error(f"Saga Failure: {e}")
            await self._compensate(saga)
            return self._build_outcome(
                "FAILED",
                transaction_id,
                saga,
                str(e),
                gate_status=self.last_gate_status,
                gate_reasons=self.last_gate_reasons,
            )

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
            utility_function=lambda a, x: self._task_utility(task_node),
            cost_lambda=0.1,
            cost_function=lambda a: self._task_cost(task_node),
        )
        self.last_counterfactual_scores.append(utility_score)
        logger.info(f"Counterfactual do({tool_name}) evaluation score: {utility_score}")
        if utility_score < self._current_counterfactual_threshold:
            raise GovernanceGateError(
                "counterfactual_score_below_threshold",
                "BLOCK",
                ["counterfactual_score_below_threshold"],
            )

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
        gate_status: str = "ALLOW",
        gate_reasons: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "transaction_id": transaction_id,
            "error": error,
            "gate_status": gate_status,
            "gate_reasons": gate_reasons or ["all_guards_passed"],
            "cognitive_preflight": self.last_cognitive_preflight,
            "steps": [{"task_id": step.task_id, "status": step.status} for step in saga.steps],
        }

    def _cognitive_preflight_enabled(self, dag_root: Any) -> bool:
        explicit = dag_root.get("cognitive_preflight")
        if explicit is not None:
            return self._parse_bool(explicit, False)
        return self._parse_bool(os.getenv("DUMMIE_COGNITIVE_PREFLIGHT"), False)

    async def _run_cognitive_preflight(self, request: GatewayRequest) -> Dict[str, Any]:
        try:
            recall = await self._execute_local_reasoning(
                "local.semantic_recall",
                {
                    "goal": request.goal,
                    "query": request.goal,
                    "top_k": 10,
                    "sources": ["mcp", "knowledge", "4d_tes"],
                },
            )
            candidates = recall.get("candidates", []) if isinstance(recall, dict) else []
            rerank = await self._execute_local_reasoning(
                "local.reasoned_rerank",
                {
                    "goal": request.goal,
                    "candidates": candidates,
                    "max_selected": 5,
                    "mode": "shadow",
                },
            )
            ranked = rerank.get("ranked", []) if isinstance(rerank, dict) else []
            packet = await self._execute_local_reasoning(
                "local.context_shaper",
                {
                    "goal": request.goal,
                    "ranked": ranked,
                    "token_budget": 4000,
                    "cloud_agent": "generic",
                },
            )
            selected_tools = packet.get("selected_tools", []) if isinstance(packet, dict) else []
            return {
                "status": "READY",
                "selected_tools": selected_tools,
                "recall_candidates": len(candidates),
                "provider_status": rerank.get("provider_status", "unknown") if isinstance(rerank, dict) else "unknown",
                "context_packet": packet if isinstance(packet, dict) else {},
            }
        except Exception as exc:
            logger.warning(f"Cognitive preflight degraded: {exc}")
            return {"status": "DEGRADED", "reason": str(exc)}

    async def _execute_local_reasoning(self, target: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if not self.mcp_gateway or not hasattr(self.mcp_gateway, "call_tool"):
            raise RuntimeError("mcp_gateway_unavailable")
        response = await self.mcp_gateway.call_tool(
            "dummie-brain",
            "dummie_execute_capability",
            {
                "target": target,
                "arguments": arguments,
            },
        )
        payload = self._parse_gateway_payload(response)
        if isinstance(payload, dict) and payload.get("error"):
            raise RuntimeError(str(payload["error"]))
        return payload

    def _parse_gateway_payload(self, value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            if "result" in value:
                return self._parse_gateway_payload(value["result"])
            if "content" in value and isinstance(value["content"], list):
                texts = [item.get("text", "") for item in value["content"] if item.get("type") == "text"]
                return self._parse_gateway_payload("\n".join(texts))
            return value
        if isinstance(value, str):
            stripped = value.strip()
            try:
                parsed = json.loads(stripped)
                return parsed if isinstance(parsed, dict) else {"value": parsed}
            except json.JSONDecodeError:
                return {"raw": stripped}
        return {"value": value}

    def _evaluate_runtime_guards(self, dag_root: Any):
        try:
            from runtime_guards import GuardInput, evaluate_runtime_guards
        except ImportError:
            from layers.l2_brain.runtime_guards import GuardInput, evaluate_runtime_guards

        return evaluate_runtime_guards(
            GuardInput(
                provider_ready=self._parse_bool(dag_root.get("provider_ready"), True),
                memory_locked=self._parse_bool(dag_root.get("memory_locked"), False),
                parent_spec_approved=self._parse_bool(dag_root.get("parent_spec_approved"), True),
                l3_policy=str(dag_root.get("l3_policy") or "ALLOWED"),
            )
        )

    def _build_hypothesis_bundle(self, dag_root: Any, bundle_id: str, bundle_cls: Any, hypothesis_cls: Any):
        bundle_node = dag_root.find("hypothesis_bundle")
        threshold = 1.5
        if bundle_node is None:
            return (
                bundle_cls(
                    bundle_id=bundle_id,
                    hypotheses=[
                        hypothesis_cls(hypothesis_id="optimal_path", content="Ejecución óptima directa", weight=0.7),
                        hypothesis_cls(hypothesis_id="fallback_path", content="Reintento o compensación parcial", weight=0.2),
                        hypothesis_cls(hypothesis_id="abort_path", content="Fallo irrecuperable", weight=0.1),
                    ],
                ),
                threshold,
            )

        threshold = self._parse_float(bundle_node.get("entropy_threshold"), 0.5)
        hypotheses = []
        for idx, node in enumerate(bundle_node.findall("hypothesis"), start=1):
            hypotheses.append(
                hypothesis_cls(
                    hypothesis_id=str(node.get("id") or f"h{idx}"),
                    content=(node.text or "").strip() or f"Hypothesis {idx}",
                    weight=self._parse_float(node.get("weight"), 1.0),
                )
            )

        if not hypotheses:
            hypotheses.append(hypothesis_cls(hypothesis_id="default", content="Default path", weight=1.0))
        return bundle_cls(bundle_id=bundle_id, hypotheses=hypotheses), threshold

    def _task_utility(self, task_node: Any) -> float:
        return self._parse_float(task_node.get("utility"), 1.0 if task_node.get("tool") else 0.0)

    def _task_cost(self, task_node: Any) -> float:
        explicit = task_node.get("cost")
        if explicit is not None:
            return self._parse_float(explicit, 0.1)

        destructive = self._parse_bool(task_node.get("destructive"), False)
        tool_name = str(task_node.get("tool") or "").lower()
        if destructive or tool_name in {"delete", "remove", "write", "overwrite"}:
            return 2.0
        return 0.1

    @staticmethod
    def _parse_bool(value: Any, default: bool) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _parse_float(value: Any, default: float) -> float:
        if value is None:
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default


class _AllowAllAuditor(BaseAuditor):
    async def audit(self, dag_xml: str, goal: str = ""):
        return True, "BYPASS"


class _NoopExecutor(BaseExecutor):
    async def execute(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": True}


class GovernanceGateError(RuntimeError):
    def __init__(self, message: str, gate_status: str, reasons: List[str]):
        super().__init__(message)
        self.gate_status = gate_status
        self.reasons = reasons
