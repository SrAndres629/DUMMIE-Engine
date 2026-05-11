import logging
from layers.l2_brain.metacognition.contracts import MetacognitiveFrame, AuthorityLevel

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

class PromptRefinerHook:
    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        raw = " ".join(frame.raw_user_input.split())
        if not raw:
            frame.missing_context.append("raw_user_input")
            frame.telemetry["refined_prompt"] = ""
            return frame

        objective = frame.strategic_objective or "Clarify objective before action"
        frame.telemetry["refined_prompt"] = (
            f"Objective: {objective}. User request: {raw}. "
            "Return operational plan, risks, required tools, verification, and next action."
        )
        frame.telemetry["prompt_refiner_provider"] = "deterministic"
        return frame

class AuthorityClassifierHook:
    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        raw = frame.raw_user_input.lower()
        if any(k in raw for k in ["borra", "delete", "remove", "root", "format", "destroy", "sudo"]):
            frame.authority_level = AuthorityLevel.A5_CRITICAL_OP
        elif any(k in raw for k in ["publica", "post", "send", "tweet", "publish", "deploy", "social"]):
            frame.authority_level = AuthorityLevel.A4_EXTERNAL_ACTOR
        elif any(k in raw for k in ["instala", "install", "setup", "configure", "apt", "npm", "pip"]):
            frame.authority_level = AuthorityLevel.A3_STATION_OP
        elif any(k in raw for k in ["crea", "edit", "write", "modify", "refactor", "fix", "patch", "update"]):
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

class ToolNeedDetectorHook:
    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        raw = frame.raw_user_input.lower()
        tools = set(frame.required_tools)

        if any(k in raw for k in ["facebook", "instagram", "tiktok", "social", "publica", "post"]):
            tools.update({"browser_driver", "social_media_api", "scheduler", "authority_gate"})
        if any(k in raw for k in ["automat", "script", "workflow"]):
            tools.update({"mission_planner", "workstation_operator", "verification_runner"})
        if any(k in raw for k in ["instala", "install", "setup", "driver"]):
            tools.update({"tool_installer", "backup_tool"})
        if any(k in raw for k in ["borra", "delete", "remove", "root"]):
            tools.update({"backup_tool", "authority_gate"})

        frame.required_tools = sorted(tools)
        if not frame.required_tools:
            frame.missing_context.append("required_tools")
        return frame
