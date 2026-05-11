import logging
import asyncio
import uuid
import hashlib
import json
import xml.etree.ElementTree as ET
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

from layers.l2_brain.gateway_contract import GatewayRequest, SagaTransaction, SagaStep
from layers.l2_brain.model_router import ModelTier

logger = logging.getLogger("dummie.brain.orchestrator")

class GovernanceGateError(Exception):
    def __init__(self, message: str, gate_status: str, reasons: List[str]):
        super().__init__(message)
        self.gate_status = gate_status
        self.reasons = reasons

class CognitiveOrchestrator:
    """
    [L2_BRAIN] Orquestador de Sagas Cognitivas.
    Maneja el flujo de ejecución de una petición desde la validación hasta la ejecución física.
    """
    def __init__(self, daemon: Any):
        self.daemon = daemon

    async def execute_request(self, request: GatewayRequest) -> Dict[str, Any]:
        """
        Ejecuta una petición completa bajo el patrón Saga.
        """
        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        transaction_id = f"TXN-{ts}-{uuid.uuid4().hex[:8]}"
        payload = f"{request.session_id}:{transaction_id}".encode("utf-8")
        context_token = "TOKEN-" + hashlib.sha256(payload).hexdigest()[:24]
        
        saga = SagaTransaction(transaction_id=transaction_id, context_token=context_token)
        self.daemon.active_transactions[transaction_id] = saga
        
        # Reset daemon state for this transaction (simplified for now)
        self.daemon.last_gate_status = "ALLOW"
        self.daemon.last_gate_reasons = ["all_guards_passed"]
        self.daemon.last_cognitive_preflight = {"status": "SKIPPED"}
        
        logger.info(f"Saga Start: {transaction_id} | Goal: {request.goal}")

        try:
            # 1. Domain Validation
            from layers.l2_brain.domain.dtos import HypothesisBundle, Hypothesis
            from layers.l2_brain.domain.hypothesis_service import HypothesisService
            
            # 2. Triple Shield Audit
            for shield, name in [(self.daemon.s_shield, "S"), (self.daemon.e_shield, "E"), (self.daemon.l_shield, "L")]:
                if shield:
                    ok, msg = await shield.audit(request.dag_xml, request.goal)
                    if not ok:
                        raise RuntimeError(f"VETO [{name}]: {msg}")

            root = ET.fromstring(request.dag_xml)
            
            # 3. Runtime Guards
            guard_decision = self.daemon._evaluate_runtime_guards(root)
            if guard_decision.status != "ALLOW":
                raise GovernanceGateError("runtime_guard_blocked", guard_decision.status, list(guard_decision.reasons))

            # 4. Hypothesis Collapse
            bundle, entropy_threshold = self.daemon._build_hypothesis_bundle(root, transaction_id, HypothesisBundle, Hypothesis)
            entropy = HypothesisService.calculate_entropy(bundle)
            if not HypothesisService.should_collapse(bundle, entropy_threshold):
                raise GovernanceGateError("high_entropy_requires_review", "REVIEW", ["high_entropy_requires_review"])
            
            # 5. Metacognition (Wave 9)
            frame = None
            if self.daemon.metacognition:
                frame = await self.daemon.metacognition.preprocess(request.session_id, request.goal)
                if self.daemon.authority_gate:
                    authorized, authority_msg = await self.daemon.authority_gate.validate_intent(frame)
                    if not authorized:
                        gate_status = "REVIEW" if "VETO" not in authority_msg else "BLOCK"
                        raise GovernanceGateError("authority_gate_blocked", gate_status, [f"authority_gate:{authority_msg}"])
                frame = await self.daemon.metacognition.deliberate(frame)

            # 6. Cognitive Preflight (Meta-Gateway Recovery)
            if self.daemon._cognitive_preflight_enabled(root):
                self.daemon.last_cognitive_preflight = await self.daemon._run_cognitive_preflight(request)

            # 7. Planning & Routing
            plan = self.daemon._build_hierarchical_plan(request, root)
            
            # 8. Task Dispatch
            for idx, task in enumerate(root.findall("task"), start=1):
                route = self.daemon._route_task_with_plan(task, plan, idx)
                await self._dispatch_task(task, saga)

            # 9. Success Outcome
            outcome = self.daemon.evaluator.build_outcome("SUCCESS", transaction_id, saga)
            
            if self.daemon.metacognition and frame:
                final_frame = await self.daemon.metacognition.postprocess(frame, outcome)
                outcome = self.daemon.evaluator.enrich_with_metacognition(outcome, final_frame)

            return outcome

        except GovernanceGateError as e:
            return self.daemon.evaluator.build_outcome("FAILED", transaction_id, saga, str(e), gate_status=e.gate_status, gate_reasons=e.reasons)
        except Exception as e:
            logger.error(f"Saga Failure: {e}", exc_info=True)
            # await self.daemon._compensate(saga) # To be moved later
            return self.daemon.evaluator.build_outcome("FAILED", transaction_id, saga, str(e))

    async def _dispatch_task(self, task_node: Any, saga: SagaTransaction):
        task_id = task_node.get("id")
        step = SagaStep(task_id=task_id)
        saga.steps.append(step)

        # [COGNITIVE LOOP] Inferencia Contrafactual do(a) Pearl
        from layers.l2_brain.domain.counterfactual_service import CounterfactualService
            
        tool_name = task_node.get("tool")
        utility_score = CounterfactualService.evaluate_intervention(
            action_a=tool_name,
            context_x=saga.transaction_id,
            utility_function=lambda a, x: self.daemon._task_utility(task_node),
            cost_lambda=0.1,
            cost_function=lambda a: self.daemon._task_cost(task_node),
        )
        self.daemon.last_counterfactual_scores.append(utility_score)
        
        if utility_score < self.daemon._current_counterfactual_threshold:
            raise GovernanceGateError("counterfactual_score_below_threshold", "BLOCK", ["counterfactual_score_below_threshold"])

        response = await self.daemon.muscle.execute(
            server_name=task_node.get("server", "filesystem"),
            tool_name=task_node.get("tool"),
            arguments=json.loads(task_node.find("arguments").text or "{}")
        )
        
        if "error" in response:
            step.status = "FAILED"
            raise RuntimeError(f"Physical Error in {task_id}: {response['error']}")
        
        step.status = "DONE"

    def is_preflight_enabled(self, dag_root: Any) -> bool:
        import os
        explicit = dag_root.get("cognitive_preflight")
        if explicit is not None:
            return self.daemon._parse_bool(explicit, False)
        return self.daemon._parse_bool(os.getenv("DUMMIE_COGNITIVE_PREFLIGHT"), False)

    async def run_preflight(self, request: GatewayRequest) -> Dict[str, Any]:
        try:
            recall = await self.call_local_reasoning(
                "local.semantic_recall",
                {"goal": request.goal, "query": request.goal, "top_k": 10, "sources": ["mcp", "knowledge", "4d_tes"]}
            )
            candidates = recall.get("candidates")
            rerank = await self.call_local_reasoning("local.reasoned_rerank", {"goal": request.goal, "candidates": candidates, "max_selected": 5, "mode": "shadow"})
            ranked = rerank.get("ranked")
            shaped = await self.call_local_reasoning("local.context_shaper", {"goal": request.goal, "ranked": ranked, "token_budget": 4000, "cloud_agent": "daemon"})
            
            selected_tools = shaped.get("selected_tools") or [str(item.get("id")) for item in ranked[:5] if item.get("id")]
            return {"status": "READY", "selected_tools": selected_tools, "context_packet": shaped}
        except Exception as exc:
            logger.warning("Cognitive preflight degraded: %s", exc)
            return {"status": "DEGRADED", "error": str(exc), "selected_tools": []}

    async def call_local_reasoning(self, target: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if not self.daemon.mcp_gateway: raise RuntimeError("mcp_gateway_unavailable")
        response = await self.daemon.mcp_gateway.call_tool("dummie-brain", "dummie_execute_capability", {"target": target, "arguments": arguments})
        return self.daemon._parse_gateway_payload(response)
