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
            frame.authority_level = AuthorityLevel.OVERSEER
        elif any(k in raw for k in ["publica", "post", "send", "tweet", "publish", "deploy", "social", "tiktok", "facebook", "instagram"]):
            frame.authority_level = AuthorityLevel.ARCHITECT
        elif any(k in raw for k in ["instala", "install", "setup", "configure", "apt", "npm", "pip"]):
            frame.authority_level = AuthorityLevel.ENGINEER
        elif any(k in raw for k in ["crea", "edit", "write", "modify", "refactor", "fix", "patch", "update"]):
            frame.authority_level = AuthorityLevel.ENGINEER
        else:
            frame.authority_level = AuthorityLevel.AGENT

        logger.info(f"Authority classified: {frame.authority_level}")
        return frame
class ContextEnricherHook:
    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        # Placeholder for real context search (memory, filesystem)
        frame.telemetry["context_scan"] = "COMPLETED"
        return frame

EXTERNAL_ACTIONS = {
    "social_media": {"browser_driver", "social_media_api", "scheduler"},
    "destructive": {"backup_tool", "system_operator"},
    "installer": {"tool_installer", "backup_tool"},
    "automation": {"mission_planner", "workstation_operator", "verification_runner"},
}

EXTERNAL_KEYWORDS = {
    "social_media": ["facebook", "instagram", "tiktok", "social", "publica", "post", "tweet", "publicar", "twittear"],
    "destructive": ["borra", "delete", "remove", "root", "format", "destroy", "sudo", "wipe", "rm"],
    "installer": ["instala", "install", "setup", "driver", "apt", "npm", "pip", "configure"],
    "automation": ["automat", "script", "workflow", "deploy"],
}

BLOCKED_AUTHORITY_ACTIONS = {
    AuthorityLevel.AGENT: {"social_media", "destructive", "installer"},
    AuthorityLevel.ENGINEER: {"social_media", "destructive"},
    AuthorityLevel.ARCHITECT: set(),
    AuthorityLevel.OVERSEER: set(),
    AuthorityLevel.HUMAN: set(),
}

class ToolNeedDetectorHook:
    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        raw = frame.raw_user_input.lower()
        tools = set(frame.required_tools)
        matched_categories = set()

        for category, keywords in EXTERNAL_KEYWORDS.items():
            if any(k in raw for k in keywords):
                tools.update(EXTERNAL_ACTIONS[category])
                matched_categories.add(category)

        frame.required_tools = sorted(tools)

        blocked = BLOCKED_AUTHORITY_ACTIONS.get(frame.authority_level, set())
        critical = matched_categories & blocked
        if critical:
            frame.risk_level = "critical"
            frame.blocked_reason = (
                f"Action blocked: {', '.join(sorted(critical))} "
                f"requires authority >= ARCHITECT (current: {frame.authority_level.name})"
            )
            logger.warning(frame.blocked_reason)

        if not frame.required_tools:
            frame.missing_context.append("required_tools")
        return frame
