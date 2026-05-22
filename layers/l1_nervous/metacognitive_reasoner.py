import json
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from layers.l1_nervous.capability_index import CapabilityIndex
from layers.l1_nervous.intelligent_intent_router import (
    IntentClassifier,
    IntentRouter,
    Intent,
    Resolution,
)
from layers.l1_nervous.local_llm_bridge import LocalLLMBridge, LLMDecision
from layers.l1_nervous.context_enricher import ContextEnricher, SessionContext
from layers.l1_nervous.smart_research_engine import SmartResearchEngine
from layers.l1_nervous.intelligence_evaluator import IntelligenceEvaluator

logger = logging.getLogger("dummie-mcp.metacognitive-reasoner")


@dataclass
class MCIRResult:
    query: str = ""
    found: bool = False
    match: Optional[dict] = None
    intent: Optional[Intent] = None
    llm_decision: Optional[LLMDecision] = None
    metacognitive_questions: List[str] = field(default_factory=list)
    research_results: Optional[dict] = None
    message: str = ""
    latency_ms: float = 0.0
    stage: str = "classifier"

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "found": self.found,
            "match": self.match,
            "intent": {
                "domain": self.intent.domain if self.intent else "",
                "action": self.intent.action if self.intent else "",
                "confidence": self.intent.confidence if self.intent else 0,
            }
            if self.intent
            else {},
            "llm_used": self.llm_decision is not None,
            "llm_suggested_tool": self.llm_decision.suggested_tool
            if self.llm_decision
            else None,
            "llm_confidence": self.llm_decision.confidence if self.llm_decision else 0,
            "metacognitive_questions": self.metacognitive_questions,
            "research_triggered": self.research_results is not None,
            "stage": self.stage,
            "message": self.message,
            "latency_ms": self.latency_ms,
        }


class MetacognitiveReasoner:
    def __init__(self):
        self._classifier = IntentClassifier()
        self._llm = LocalLLMBridge()
        self._context = ContextEnricher()
        self._research = SmartResearchEngine()
        self._evaluator = IntelligenceEvaluator()
        self._router_cache: Optional[IntentRouter] = None

    def analyze(
        self,
        query: str,
        index: CapabilityIndex,
        session_id: str = "default",
    ) -> MCIRResult:
        start = time.time()
        result = MCIRResult(query=query)

        self._context.record_query(query, session_id)

        router = IntentRouter(index)
        resolution = router.resolve(query)

        result.intent = resolution.intent
        result.message = resolution.message

        if resolution.found and resolution.match:
            result.found = True
            result.match = resolution.match
            result.stage = "exact_match"
            result.latency_ms = (time.time() - start) * 1000

            self._evaluator.log_decision(result.to_dict())
            return result

        result.stage = "llm_reasoning"
        ctx = self._context.get_context(session_id)
        tools_summary = self._summarize_tools(index)
        skills_summary = self._summarize_skills(index)

        llm_decision = self._llm.reason(
            query=query,
            context=ctx.to_dict(),
            tools_summary=tools_summary,
            skills_summary=skills_summary,
        )
        result.llm_decision = llm_decision

        if llm_decision.suggested_tool and llm_decision.confidence >= 0.6:
            tool = index.find_exact_match(
                resolution.intent.domain, resolution.intent.action
            )
            if not tool:
                tool = {"id": llm_decision.suggested_tool, "type": "llm_suggested"}
            result.found = True
            result.match = tool
            result.message = (
                f"LLM sugirio: {llm_decision.suggested_tool} "
                f"(confianza: {llm_decision.confidence:.2f})"
            )
            result.stage = "llm_match"
            result.metacognitive_questions = llm_decision.metacognitive_questions

            self._evaluator.log_decision(result.to_dict())
            result.latency_ms = (time.time() - start) * 1000
            return result

        if llm_decision.adaptation:
            result.message = (
                f"Sin match exacto. Sugerencia de adaptacion: {llm_decision.adaptation}"
            )
            result.metacognitive_questions = llm_decision.metacognitive_questions
            result.stage = "adaptation_suggested"

            self._evaluator.log_decision(result.to_dict())
            result.latency_ms = (time.time() - start) * 1000
            return result

        if llm_decision.metacognitive_questions or llm_decision.needs_more_context:
            result.metacognitive_questions = llm_decision.metacognitive_questions
            result.message = (
                "Se necesita mas contexto para determinar la herramienta correcta."
            )
            if llm_decision.needs_more_context:
                result.message += (
                    f" Campos faltantes: {', '.join(llm_decision.needs_more_context)}"
                )
            result.stage = "needs_more_context"

            self._evaluator.log_decision(result.to_dict())
            result.latency_ms = (time.time() - start) * 1000
            return result

        result.stage = "research"
        domain = resolution.intent.domain
        action = resolution.intent.action
        research_results = self._research.search(
            domain=domain, action=action, query=query
        )
        result.research_results = research_results

        if research_results and research_results.get("results"):
            top = research_results["results"][0]
            result.message = (
                f"Investigacion completada. Mejor resultado: {top.get('name', 'N/A')} "
                f"({top.get('stars', 0)} estrellas). "
                f"URL: {top.get('url', 'N/A')}. "
                f"Iniciar plan de integracion: dummie_execute_capability(target='research.integrate_plan', ...)"
            )
            result.stage = "research_complete"
        else:
            result.message = (
                f"No se encontro herramienta para '{resolution.intent.to_key()}'. "
                f"GitHub no mostro resultados relevantes."
            )
            result.stage = "no_results"

        self._evaluator.log_decision(result.to_dict())
        result.latency_ms = (time.time() - start) * 1000
        return result

    def _summarize_tools(self, index: CapabilityIndex) -> str:
        lines = []
        count = 0
        for cat, tools in index.list_all().items():
            for t in tools:
                lines.append(f"- {t['id']}: {t.get('description', '')[:100]}")
                count += 1
                if count >= 30:
                    lines.append(
                        f"... y {index.sum_index()['total_capabilities'] - 30} mas"
                    )
                    return "\n".join(lines)
        return "\n".join(lines)

    def _summarize_skills(self, index: CapabilityIndex) -> str:
        lines = []
        for s in index.list_skills()[:15]:
            cats = ", ".join(s.get("capabilities", []))
            lines.append(f"- {s['id']}: {s.get('description', '')[:80]} [{cats}]")
        return "\n".join(lines)
