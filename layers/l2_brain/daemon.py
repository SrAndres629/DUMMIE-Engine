__spec_id__ = "DE-V2-L2-42B"
__spec_id__ = "DE-V2-L2-34"
__spec_id__ = "DE-V2-L2-27B"
__spec_id__ = "DE-V2-L2-27"
__spec_id__ = "DE-V2-L2-40B"
__spec_id__ = "DE-V2-L2-28"
__spec_id__ = "DE-V2-L2-37"
__spec_id__ = "DE-V2-L2-40"
__spec_id__ = "DE-V2-L2-31"
__spec_id__ = "DE-V2-L2-09"
__spec_id__ = "DE-V2-L2-41B"
__spec_id__ = "DE-V2-L2-39"
__spec_id__ = "DE-V2-L2-42"
__spec_id__ = "DE-V2-L2-21"
__spec_id__ = "DE-V2-L2-29"
__spec_id__ = "DE-V2-L2-36"
__spec_id__ = "DE-V2-L2-38"
import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional
from model_router import ModelTier
from datetime import datetime
from abc import ABC, abstractmethod

# Importaciones Isomórficas (Flat Structure)
from gateway_contract import GatewayRequest, SagaTransaction, SagaStep
from auditor_port import BaseAuditor, BaseExecutor

# Importaciones de Adaptadores (Cruce de Capas vía PYTHONPATH)
try:
    from safe_fallbacks import FailClosedAuditor, FailClosedExecutor
except ImportError:
    from layers.l2_brain.safe_fallbacks import FailClosedAuditor, FailClosedExecutor

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

try:
    from event_bus import AsyncEventBus
except ImportError:
    from layers.l2_brain.event_bus import AsyncEventBus

try:
    from repo_guard import RepoGuard
except ImportError:
    from layers.l1_nervous.repo_guard import RepoGuard

class DummieDaemon:
    """
    [L2_BRAIN] Orquestador Supremo Antigravity.
    Estructura Tabula Rasa: Flat, Determinista e Industrial.
    """
    def __init__(
        self,
        ledger_path: str,
        mcp_gateway: Any,
        event_bus: AsyncEventBus,
        skill_binder: Optional[Any] = None,
        event_store: Optional[Any] = None,
        model_router: Optional[Any] = None,
        model_executor: Optional[Any] = None,
        semantic_cache: Optional[Any] = None,
        neuron_ledger: Optional[Any] = None,
        action_graph: Optional[Any] = None,
        supervisor_protocol: Optional[Any] = None,
        entity_voice: Optional[Any] = None,
        auto_evolver: Optional[Any] = None,
    ):
        self.ledger_path = ledger_path
        self.mcp_gateway = mcp_gateway
        self.event_bus = event_bus
        self.skill_binder = skill_binder
        self.event_store = event_store
        self.model_router = model_router
        self.model_executor = model_executor
        self.semantic_cache = semantic_cache
        self.neuron_ledger = neuron_ledger
        self.action_graph = action_graph
        self.supervisor_protocol = supervisor_protocol
        self.entity_voice = entity_voice
        self.auto_evolver = auto_evolver
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
        
        self._background_tasks: set[asyncio.Task] = set()
        self.request_timeout_s = float(os.getenv("DUMMIE_REQUEST_TIMEOUT_S", "60"))
        self.diagnostic_mode = os.getenv("DUMMIE_DIAGNOSTIC_MODE") == "1"

        # Capas Somáticas (Conexión Directa)
        shield_error = "shield_import_failed"
        executor_error = "muscle_import_failed"
        self.s_shield: BaseAuditor = TopologicalAuditor() if TopologicalAuditor else FailClosedAuditor(shield_error)
        self.e_shield: BaseAuditor = BudgetAuditor() if BudgetAuditor else FailClosedAuditor(shield_error)
        self.l_shield: BaseAuditor = ComplianceAuditor() if ComplianceAuditor else FailClosedAuditor(shield_error)
        self.muscle: BaseExecutor = MuscleDriver(mcp_gateway) if MuscleDriver else FailClosedExecutor(executor_error)

        if self.diagnostic_mode:
            try:
                from daemon_diagnostic import DiagnosticReporter
                self.diagnostic_reporter = DiagnosticReporter(self)
            except ImportError:
                from layers.l2_brain.daemon_diagnostic import DiagnosticReporter
                self.diagnostic_reporter = DiagnosticReporter(self)

    def _spawn_task(self, coro, transaction_hint: str = "") -> None:
        task = asyncio.create_task(coro)
        self._background_tasks.add(task)

        def _done_callback(done: asyncio.Task) -> None:
            self._background_tasks.discard(done)
            try:
                done.result()
            except Exception as exc:
                logger.exception(
                    "Background task failed transaction_hint=%s error=%s",
                    transaction_hint,
                    exc,
                )

        task.add_done_callback(_done_callback)

    async def _handle_intent(self, payload: Any):
        if not isinstance(payload, GatewayRequest):
            try:
                payload = GatewayRequest(**payload)
            except Exception as e:
                logger.error(f"Invalid intent payload: {e}")
                return
        
        self._spawn_task(
            asyncio.wait_for(
                self._process_request_safe(payload),
                timeout=self.request_timeout_s,
            ),
            transaction_hint=getattr(payload, "session_id", ""),
        )

    async def submit_intent(self, intent: GatewayRequest):
        """Método directo para que el gateway envíe intenciones sin esperar al bus."""
        await self._handle_intent(intent)

    async def run_forever(self):
        if self.diagnostic_mode:
            logger.info("Antigravity Daemon: STARTING IN DIAGNOSTIC MODE")
            await self.diagnostic_reporter.run_diagnostic()
            logger.info("Diagnostic complete. Staying in passive wait mode.")
            while True:
                await asyncio.sleep(3600)
                
        logger.info("Antigravity Daemon: ONLINE (TABULA RASA MODE)")
        self.event_bus.subscribe("INTENT", self._handle_intent)
        await self.event_bus.start()
        
        # Keep the daemon alive
        while True:
            await asyncio.sleep(3600)

    async def _process_request_safe(self, request: GatewayRequest):
        async with self.concurrency_limit:
            await self.process_request(request)

    async def process_request(self, request: GatewayRequest):
        import uuid
        import hashlib
        from datetime import UTC
        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        transaction_id = f"TXN-{ts}-{uuid.uuid4().hex[:8]}"
        payload = f"{request.session_id}:{transaction_id}".encode("utf-8")
        context_token = "TOKEN-" + hashlib.sha256(payload).hexdigest()[:24]
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

    async def reason_with_tiers(self, prompt: str, system_prompt: str = "", concept: str = "general", saga_id: str = "unknown") -> str:
        """
        [L2_BRAIN] Razonamiento agéntico multinivel con ahorro de tokens.
        """
        if not self.model_router or not self.model_executor:
            return "DEGRADED_MODE: No model router/executor"

        # 0. Check Semantic Cache
        if self.semantic_cache:
            cached = await self.semantic_cache.get(prompt, system_prompt)
            if cached:
                return cached

        # 1. Routing & Tiers
        decision = self.model_router.route(prompt)
        tiers_to_try = [decision.tier, ModelTier.CLOUD_STD, ModelTier.LOCAL_FAST]
        
        # Identity injection
        if self.entity_voice and not system_prompt:
            system_prompt = self.entity_voice.get_system_prompt(concept)
            
        last_error = "No models available"
        for tier in tiers_to_try:
            configs = self.model_router.registry.models.get(tier, [])
            for config in configs:
                try:
                    logger.info(f"Reasoning: Trying {config.model_id} ({tier.value})...")
                    
                    # 2. Execution
                    response = await self.model_executor.execute_config(config, prompt, system_prompt, concept)
                    
                    # 3. Stats & Reputation (Wave 4)
                    if self.neuron_ledger:
                        if response.success:
                            self.neuron_ledger.record_success(config.model_id, response.latency_ms)
                        else:
                            self.neuron_ledger.record_failure(config.model_id, response.error or "unknown")

                    if response.success:
                        # 4. Action Graph (Wave 4)
                        if self.action_graph:
                            from action_graph import ActionNode
                            import uuid
                            await self.action_graph.record_action(ActionNode(
                                action_id=uuid.uuid4().hex[:8],
                                saga_id=saga_id,
                                model_id=config.model_id,
                                action_type="REASON",
                                target="llm_inference",
                                description=f"Razonamiento tier {tier.value} para: {prompt[:50]}..."
                            ))
                        
                        # 5. Supervision (Wave 4)
                        if self.supervisor_protocol and tier != ModelTier.LOCAL_FAST:
                            review = await self.supervisor_protocol.review_task(prompt, response.text, config.model_id)
                            if self.neuron_ledger:
                                if review.approved:
                                    self.neuron_ledger.reward(config.model_id, amount=review.score * 10)
                                else:
                                    self.neuron_ledger.penalize(config.model_id, amount=20.0)

                        # 6. Save to Cache
                        final_text = response.text
                        if self.entity_voice:
                            final_text = self.entity_voice.format_output(final_text, config.model_id)
                            
                        if self.semantic_cache:
                            await self.semantic_cache.set(prompt, final_text, system_prompt)

                        return final_text
                    else:
                        last_error = response.error
                            
                except Exception as e:
                    logger.error(f"Error in tier {tier}: {e}")
                    last_error = str(e)
        
        # [WAVE 6] Self-Healing Trigger
        if self.auto_evolver:
            logger.warning("Critical Reasoning Failure: Triggering Auto-Evolution Analysis...")
            analysis = await self.auto_evolver.analyze_failure({
                "message": last_error,
                "stack_trace": f"Reasoning loop failed for prompt: {prompt[:100]}"
            })
            # Log for the user to see DUMMIE's internal thought
            logger.info(f"DUMMIE Self-Healing Analysis: {analysis['root_cause']}")

                    
        return f"ERROR_EXECUTION: {last_error}"

    async def _execute_local_reasoning(self, target: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        [BRIDGE] Ejecuta razonamiento local.
        Si es una capacidad nativa (mcp), la llama. 
        Si no, intenta usar el ModelRouter para razonar sobre el problema.
        """
        try:
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
            return self._parse_gateway_payload(response)
        except Exception as e:
            logger.info(f"Local capability {target} failed or unavailable ({e}). Falling back to Tiered Reasoning.")
            # Fallback a razonamiento generativo si la herramienta falla
            prompt = f"Analiza esta tarea y devuelve un JSON válido: {target} con argumentos {arguments}"
            result_text = await self.reason_with_tiers(prompt, "Eres el cerebro de DUMMIE Engine. Devuelve solo JSON.", concept=f"fallback_{target}")
            return self._parse_gateway_payload(result_text)

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


# Classes _FallbackUnsafeAuditor and _NoopExecutor moved to safe_fallbacks.py


class GovernanceGateError(RuntimeError):
    def __init__(self, message: str, gate_status: str, reasons: List[str]):
        super().__init__(message)
        self.gate_status = gate_status
        self.reasons = reasons
