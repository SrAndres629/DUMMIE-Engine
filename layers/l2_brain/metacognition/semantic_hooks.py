import logging
from typing import Any
from .contracts import MetacognitiveFrame

logger = logging.getLogger("dummie.metacognition.input_hooks")

class SemanticToolSelectorHook:
    def __init__(self, mcp_gateway: Any):
        self.mcp_gateway = mcp_gateway

    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        """
        Usa embeddings para encontrar herramientas relevantes al objetivo.
        """
        if not self.mcp_gateway:
            return frame
            
        logger.info(f"Semantically searching tools for: {frame.raw_user_input}")
        
        try:
            from embedding_provider import EmbeddingProvider
            query_vec = EmbeddingProvider.generate_vector(frame.raw_user_input)
            
            # Buscamos en el meta-gateway
            frame.telemetry["semantic_tool_search"] = "INITIALIZED"
            
        except Exception as e:
            logger.error(f"Semantic tool selection failed: {e}")
            
        return frame
