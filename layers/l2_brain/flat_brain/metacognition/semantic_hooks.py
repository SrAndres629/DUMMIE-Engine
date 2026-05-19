import logging
from typing import Any
from layers.l2_brain.metacognition.contracts import MetacognitiveFrame

logger = logging.getLogger("dummie.metacognition.input_hooks")

class SemanticToolSelectorHook:
    def __init__(self, mcp_gateway: Any):
        from layers.l2_brain.metagateway_adapter import MetaGatewayAdapter
        self.adapter = MetaGatewayAdapter(mcp_gateway)

    async def run(self, frame: MetacognitiveFrame) -> MetacognitiveFrame:
        """
        Usa embeddings para encontrar herramientas relevantes al objetivo.
        """
        if not self.adapter.gateway:
            return frame
            
        logger.info(f"Semantically searching tools for: {frame.raw_user_input}")
        
        try:
            # Buscamos en el meta-gateway vía descubrimiento semántico
            discovery_result = await self.adapter.discover_capabilities(frame.raw_user_input)
            
            if discovery_result.get("success") and "capabilities" in discovery_result:
                tools = discovery_result["capabilities"]
                frame.required_tools.extend([t["id"] for t in tools if t.get("id")])
                frame.telemetry["semantic_tool_search"] = f"FOUND_{len(tools)}"
                logger.info(f"Metacognitive discovery found {len(tools)} potential tools")
            elif discovery_result.get("error"):
                logger.warning(f"Metacognitive discovery failed: {discovery_result['error']}")
                frame.telemetry["semantic_tool_search"] = "GATEWAY_ERROR"
                frame.telemetry["semantic_tool_error"] = discovery_result["error"]
            else:
                frame.telemetry["semantic_tool_search"] = "NO_RESULTS"
            
        except Exception as e:
            logger.error(f"Semantic tool selection logic failed: {e}")
            frame.telemetry["semantic_tool_search"] = "INTERNAL_ERROR"
            
        return frame
