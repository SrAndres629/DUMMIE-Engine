import logging
from typing import Any
from layers.l2_brain.metacognition.contracts import MetacognitiveFrame

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
            from layers.l2_brain.embedding_provider import EmbeddingProvider
            query_vec = EmbeddingProvider.generate_vector(frame.raw_user_input)
            
            # Buscamos en el meta-gateway vía descubrimiento semántico
            # El Gateway de DUMMIE expone dummie_discover_capabilities
            try:
                discovery_result = await self.mcp_gateway.execute_tool(
                    server_name="dummie-brain",
                    tool_name="dummie_discover_capabilities",
                    arguments={"query": frame.raw_user_input}
                )
                
                if discovery_result and "capabilities" in discovery_result:
                    tools = discovery_result["capabilities"]
                    frame.required_tools.extend([t["id"] for t in tools if t.get("id")])
                    frame.telemetry["semantic_tool_search"] = f"FOUND_{len(tools)}"
                    logger.info(f"Metacognitive discovery found {len(tools)} potential tools")
                else:
                    frame.telemetry["semantic_tool_search"] = "NO_RESULTS"
            except Exception as ge:
                logger.warning(f"Metacognitive discovery tool call failed: {ge}")
                frame.telemetry["semantic_tool_search"] = "GATEWAY_ERROR"
            
        except Exception as e:
            logger.error(f"Semantic tool selection logic failed: {e}")
            
        return frame
