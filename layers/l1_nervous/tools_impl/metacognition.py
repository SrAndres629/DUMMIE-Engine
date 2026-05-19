import json
from typing import Any, Dict, List
from mcp.server.fastmcp import FastMCP
from layers.l2_brain.metacognition.contracts import MetacognitiveFrame

class MetacognitionToolService:
    def __init__(self, orchestrator: Any):
        self.orchestrator = orchestrator
        self.pipeline = getattr(orchestrator, "metacognition", None)

    async def refine_prompt(self, prompt: str) -> str:
        if not self.pipeline:
            return json.dumps({"refined_intent": "", "refined_prompt": ""})
        frame = await self.pipeline.preprocess("test_session", prompt)
        return json.dumps({
            "refined_intent": frame.refined_intent,
            "refined_prompt": frame.telemetry.get("refined_prompt", "")
        })

    async def plan_mission(self, prompt: str) -> str:
        if not self.pipeline:
            return json.dumps({"mission_plan": []})
        frame = await self.pipeline.preprocess("test_session", prompt)
        frame = await self.pipeline.deliberate(frame)
        return json.dumps({
            "mission_plan": frame.mission_plan
        })

    async def criticize_plan(self, plan: List[Dict[str, Any]]) -> str:
        if not self.pipeline:
            return json.dumps({"deliberation_summary": ""})
        frame = MetacognitiveFrame(session_id="test_session", raw_user_input="")
        frame.mission_plan = plan
        frame = await self.pipeline.deliberate(frame)
        return json.dumps({
            "deliberation_summary": frame.deliberation_summary
        })

    async def verify_answer(self, prompt: str, answer: str) -> str:
        if not self.pipeline:
            return json.dumps({"verification_findings": []})
        frame = MetacognitiveFrame(session_id="test_session", raw_user_input=prompt)
        frame = await self.pipeline.postprocess(frame, answer)
        return json.dumps({
            "verification_findings": frame.verification_findings
        })

    async def recommend_tools(self, prompt: str) -> str:
        if not self.pipeline:
            return json.dumps({"required_tools": []})
        frame = await self.pipeline.preprocess("test_session", prompt)
        return json.dumps({
            "required_tools": frame.required_tools
        })

def register_metacognitive_tools(mcp: FastMCP, orchestrator: Any):
    @mcp.tool()
    async def dummie_metacognitive_analyze(raw_input: str) -> str:
        """
        Realiza un análisis metacognitivo completo de una intención.
        Devuelve el MetacognitiveFrame refinado.
        """
        if not hasattr(orchestrator, "metacognition") or not orchestrator.metacognition:
            return "Error: Metacognitive Pipeline no disponible."
        
        frame = await orchestrator.metacognition.preprocess("internal_audit", raw_input)
        frame = await orchestrator.metacognition.deliberate(frame)
        
        return json.dumps({
            "refined_intent": frame.refined_intent,
            "strategic_objective": frame.strategic_objective,
            "authority_level": frame.authority_level,
            "mission_plan": frame.mission_plan,
            "deliberation": frame.deliberation_summary
        }, indent=2)

    @mcp.tool()
    async def dummie_authority_check(action: str) -> str:
        """
        Verifica el nivel de autoridad requerido para una acción específica.
        """
        if not hasattr(orchestrator, "metacognition") or not orchestrator.metacognition:
            return "Error: Metacognitive Pipeline no disponible."
            
        frame = await orchestrator.metacognition.preprocess("authority_check", action)
        return f"ACCIÓN: {action}\nAUTORIDAD REQUERIDA: {frame.authority_level}"
