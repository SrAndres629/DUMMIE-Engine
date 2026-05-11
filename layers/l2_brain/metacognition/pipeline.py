import logging
from typing import List, Any
from .contracts import MetacognitiveFrame

logger = logging.getLogger("dummie.metacognition.pipeline")

class Hook(property):
    pass # Placeholder for hook decorator if needed

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
        return frame

    async def deliberate(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        for hook in self.deliberation_hooks:
            try:
                frame = await hook.run(frame)
            except Exception as e:
                logger.error(f"Deliberation Hook {hook.__class__.__name__} failed: {e}")
        return frame

    async def postprocess(self, frame: MetacognitiveFrame, outcome: Any) -> MetacognitiveFrame:
        # Outcome could be the raw response from the daemon
        frame.final_response = str(outcome)
        for hook in self.output_hooks:
            try:
                frame = await hook.run(frame)
            except Exception as e:
                logger.error(f"Output Hook {hook.__class__.__name__} failed: {e}")
        return frame
