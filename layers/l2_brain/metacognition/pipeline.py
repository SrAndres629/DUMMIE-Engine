import logging
from typing import List, Any
from layers.l2_brain.metacognition.contracts import MetacognitiveFrame

logger = logging.getLogger("dummie.metacognition.pipeline")

class MetacognitivePipeline:
    def __init__(self, input_hooks=None, deliberation_hooks=None, output_hooks=None):
        self.input_hooks = input_hooks or []
        self.deliberation_hooks = deliberation_hooks or []
        self.output_hooks = output_hooks or []

    async def preprocess(self, session_id: str, raw_input: str) -> MetacognitiveFrame:
        frame = MetacognitiveFrame(session_id=session_id, raw_user_input=raw_input)
        for hook in self.input_hooks:
            try:
                frame = await hook.run(frame)
            except Exception as e:
                logger.error(f"Input Hook {hook.__class__.__name__} failed: {e}")
                self._record_hook_failure(frame, "input", hook, e)
        return frame

    async def deliberate(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        for hook in self.deliberation_hooks:
            try:
                frame = await hook.run(frame)
            except Exception as e:
                logger.error(f"Deliberation Hook {hook.__class__.__name__} failed: {e}")
                self._record_hook_failure(frame, "deliberation", hook, e)
        return frame

    async def postprocess(self, frame: MetacognitiveFrame, outcome: Any) -> MetacognitiveFrame:
        # Outcome could be the raw response from the daemon
        frame.final_response = str(outcome)
        for hook in self.output_hooks:
            try:
                frame = await hook.run(frame)
            except Exception as e:
                logger.error(f"Output Hook {hook.__class__.__name__} failed: {e}")
                self._record_hook_failure(frame, "output", hook, e)
        return frame

    @staticmethod
    def _record_hook_failure(frame: MetacognitiveFrame, phase: str, hook: Any, error: Exception) -> None:
        failures = frame.telemetry.setdefault("hook_failures", [])
        failures.append(
            {
                "phase": phase,
                "hook": hook.__class__.__name__,
                "error": str(error),
            }
        )
        frame.risk_level = "degraded"
