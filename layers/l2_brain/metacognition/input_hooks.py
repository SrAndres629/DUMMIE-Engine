import logging
from .contracts import MetacognitiveFrame, AuthorityLevel

logger = logging.getLogger("dummie.metacognition.input_hooks")

class IntentClarifierHook:
    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        # Simple heuristic for now, will be replaced by LLM call if possible
        raw = frame.raw_user_input.lower()
        if "autom" in raw or "script" in raw or "crea" in raw:
            frame.refined_intent = "OBJECTIVE_AUTOMATION"
            frame.strategic_objective = "Deploy autonomous operational workflow"
        else:
            frame.refined_intent = "OBJECTIVE_INQUIRY"
            frame.strategic_objective = "Gather system intelligence"
        return frame

class AuthorityClassifierHook:
    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        raw = frame.raw_user_input.lower()
        if "borra" in raw or "delete" in raw or "root" in raw:
            frame.authority_level = AuthorityLevel.A5_CRITICAL_OP
        elif any(k in raw for k in ["publica", "post", "send", "tiktok", "facebook", "instagram", "social"]):
            frame.authority_level = AuthorityLevel.A4_EXTERNAL_ACTOR
        elif any(k in raw for k in ["instala", "install", "chrome", "driver", "setup"]):
            frame.authority_level = AuthorityLevel.A3_STATION_OP
        elif any(k in raw for k in ["crea", "edit", "write", "modify", "refactor"]):
            frame.authority_level = AuthorityLevel.A1_WORKSPACE_OP
        else:
            frame.authority_level = AuthorityLevel.A0_OBSERVER
        
        logger.info(f"Authority classified: {frame.authority_level}")
        return frame

class ContextEnricherHook:
    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        # Placeholder for real context search (memory, filesystem)
        frame.telemetry["context_scan"] = "COMPLETED"
        return frame
