import json
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP

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
